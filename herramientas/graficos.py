"""Gráficos del canal dibujados con Pillow: intro animada, marcador, placas de texto y zócalos.

Estilo del canal (manual de estilo, 05/11): tipografía "Técnica" (JetBrains Mono para títulos, nombres y
números; IBM Plex Sans para texto descriptivo) y paleta "Forest". Placas y marcador van SOBRE VIDEO:
un tramo del partido desenfocado, oscurecido y teñido de verde (sin logos de canal: el UEFA se recorta),
nunca sobre negro liso. Cuando se nombra a alguien, va su retrato (`foto`); `formacion` arma el equipo en la cancha.

Las animaciones se renderizan cuadro a cuadro y se mandan a ffmpeg por pipe.
"""
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FPS = 30
RAIZ = Path(__file__).resolve().parent.parent
FUENTES = RAIZ / "animaciones" / "futbol" / "assets" / "fonts"
F_MONO = FUENTES / "jetbrains-mono.ttf"
F_PLEX = FUENTES / "plex-sans.ttf"

# paleta Forest
FONDO = (26, 46, 26)       # #1a2e1a
PANEL = (45, 74, 45)       # #2d4a2d
VERDE = (74, 124, 74)      # #4a7c4a
ACENTO = (122, 179, 122)   # #7ab37a
CLARO = (200, 230, 200)    # #c8e6c8
TEXTO = (242, 239, 232)    # #f2efe8
OSCURO = (14, 26, 14)
CANAL = "LOS 11"
COLOR_EQUIPO = {"LIVERPOOL": (200, 16, 46), "MILAN": (232, 232, 232), "OLYMPIACOS": (200, 16, 46),
                "JUVENTUS": (240, 240, 240), "CHELSEA": (3, 70, 148)}


def fuente(peso, tam, plex=False):
    """JetBrains Mono (o Plex Sans) con el peso pedido (son fuentes variables)."""
    clave = (peso, int(tam), plex)
    if clave not in fuente.cache:
        f = ImageFont.truetype(str(F_PLEX if plex else F_MONO), int(tam))
        f.set_variation_by_axes([peso, 100] if plex else [peso])
        fuente.cache[clave] = f
    return fuente.cache[clave]


fuente.cache = {}


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


# ---------- fondos ----------
def _fondo_liso(W, H):
    """Verde oscuro con viñeta y líneas de cancha muy tenues (para la intro o si no hay video)."""
    clave = (W, H)
    if clave not in _fondo_liso.cache:
        s = W / 1920
        img = Image.new("RGB", (W, H), OSCURO)
        luz = Image.new("L", (W, H), 0)
        ImageDraw.Draw(luz).ellipse([-W * 0.1, -H * 0.3, W * 1.1, H * 1.3], fill=255)
        from PIL import ImageFilter
        luz = luz.filter(ImageFilter.GaussianBlur(W / 6))
        img = Image.composite(Image.new("RGB", (W, H), FONDO), img, luz)
        d = ImageDraw.Draw(img, "RGBA")
        lc = ACENTO + (22,)
        d.line([W / 2, 0, W / 2, H], fill=lc, width=int(3 * s))
        r = 190 * s
        d.ellipse([W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r], outline=lc, width=int(3 * s))
        _fondo_liso.cache[clave] = img
    return _fondo_liso.cache[clave].copy()


_fondo_liso.cache = {}


def _cuadros_fondo(fondo, W, H, dur):
    """Generador de cuadros (RGB) del video de fondo: desenfocado, en cámara lenta, oscuro y teñido de verde.
    fondo = {"archivo": ruta, "desde": seg, "limpio": filtro que saca logos (de armar.filtro_limpio)}.
    Sin fondo, devuelve el fondo liso."""
    n = round(dur * FPS)
    if not fondo:
        base = _fondo_liso(W, H)
        for _ in range(n):
            yield base
        return
    s = W / 1920
    lento = 2.5
    limpio = fondo.get("limpio")  # sin logos de canal (recorte o franja tapada)
    f = (f"[0:v]{limpio + ',' if limpio else ''}setpts={lento}*PTS,fps={FPS},"
         f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
         f"gblur=sigma={22 * s:.1f},eq=brightness=-0.10:saturation=0.45,"
         f"drawbox=x=0:y=0:w=iw:h=ih:color=0x1a2e1a@0.55:t=fill,vignette=PI/4,"
         f"tpad=stop_mode=clone:stop_duration={dur:.2f}[out]")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(fondo.get("desde", 0)), "-t", f"{dur / lento + 1:.2f}",
                          "-i", str(fondo["archivo"]), "-an", "-filter_complex", f, "-map", "[out]",
                          "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         stdout=subprocess.PIPE)
    tam = W * H * 3
    ultimo = _fondo_liso(W, H)
    for _ in range(n):
        buf = p.stdout.read(tam)
        if len(buf) == tam:
            ultimo = Image.frombytes("RGB", (W, H), buf)
        yield ultimo
    p.stdout.close()
    p.wait()


def _render(dest, W, H, dur, cuadro_fn, fondo=None):
    """cuadro_fn(t, i, n) -> capa RGBA que se pone encima del fondo (o una imagen completa si la función
    dibuja su propio fondo)."""
    n = round(dur * FPS)
    p = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", "-an", str(dest)], stdin=subprocess.PIPE)
    for i, base in enumerate(_cuadros_fondo(fondo, W, H, dur)):
        capa = cuadro_fn(i / FPS, i, n)
        img = Image.alpha_composite(base.convert("RGBA"), capa) if capa.mode == "RGBA" else capa
        p.stdin.write(img.convert("RGB").tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise SystemExit(f"ffmpeg falló renderizando {dest}")


# ---------- piezas de texto ----------
def _espaciado(d, xy, txt, f, color, esp=0.0):
    """Texto con letter-spacing; devuelve el ancho."""
    x, y = xy
    for c in txt:
        d.text((x, y), c, font=f, fill=color)
        x += d.textlength(c, font=f) + esp
    return x - xy[0] - esp


def _ancho_esp(txt, f, esp):
    d = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    return sum(d.textlength(c, font=f) for c in txt) + esp * max(0, len(txt) - 1)


def _marca(d, s, alpha=255):
    """'LOS 11' arriba a la izquierda, con la barra verde (como en los gráficos de partido)."""
    f = fuente(700, 28 * s)
    d.rectangle([96 * s, 66 * s, 104 * s, 104 * s], fill=ACENTO + (alpha,))
    d.text((118 * s, 70 * s), CANAL, font=f, fill=TEXTO + (alpha,))


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


# ---------- intro del canal ----------
def intro(dest, W, H, dur=3.2, subtitulo="", fondo=None):
    """'LOS 11' se escribe letra por letra (máquina de escribir, con cursor verde), se abre la línea y
    entra GRANDE el título del video con un barrido (la última palabra en verde). Funde a negro al final."""
    s = W / 1920
    f_t = fuente(700, 150 * s)
    sub = subtitulo.upper()
    d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    tam = 120 * s
    while sub and d0.textlength(sub, font=fuente(800, tam)) > W * 0.84:
        tam -= 4 * s
    f_s = fuente(800, tam)
    ancho = d0.textlength(CANAL, font=f_t)
    x0 = W / 2 - ancho / 2
    asc, desc = f_t.getmetrics()
    y0 = H / 2 - 150 * s - asc * 0.78 if sub else H / 2 - asc * 0.78
    yl = H / 2 - 20 * s if sub else H / 2 + 92 * s
    palabras = sub.split(" ")
    resto, ultima = (" ".join(palabras[:-1]) + " ", palabras[-1]) if len(palabras) > 1 else ("", sub)
    ws = d0.textlength(sub, font=f_s)
    xs = W / 2 - ws / 2
    ys = yl + 44 * s
    capa_t = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if sub:
        dt = ImageDraw.Draw(capa_t)
        dt.text((xs, ys), resto, font=f_s, fill=TEXTO)
        dt.text((xs + d0.textlength(resto, font=f_s), ys), ultima, font=f_s, fill=ACENTO)

    def cuadro(t, i, n):
        img = _fondo_liso(W, H).convert("RGBA")
        d = ImageDraw.Draw(img)
        k = min(len(CANAL), int(max(0.0, t - 0.15) / 0.09))  # letras escritas
        txt = CANAL[:k]
        d.text((x0, y0), txt, font=f_t, fill=TEXTO)
        cx = x0 + d.textlength(txt, font=f_t) + 10 * s
        escribiendo = k < len(CANAL)
        if escribiendo or int(t * 2.5) % 2 == 0 and t < 1.0:  # cursor
            d.rectangle([cx, y0 + asc * 0.12, cx + 22 * s, y0 + asc * 0.98], fill=ACENTO)
        a = ease((t - 0.75) / 0.45)
        if a > 0:
            lw = (max(ancho, ws) / 2 + 40 * s) * a
            d.rectangle([W / 2 - lw, yl, W / 2 + lw, yl + 6 * s], fill=ACENTO)
        if sub:
            b = ease((t - 0.95) / 0.55)
            if b > 0:  # barrido de izquierda a derecha, con un leve ascenso
                corte = int(xs + (ws + 40 * s) * b)
                c = capa_t.crop((0, 0, max(1, corte), H))
                img.alpha_composite(c, (0, int((1 - b) * 14 * s)))
                if b < 1:  # borde verde del barrido
                    d = ImageDraw.Draw(img)
                    d.rectangle([corte, ys + 6 * s, corte + 8 * s, ys + tam * 0.98], fill=ACENTO)
        fin = max(0.0, (t - (dur - 0.45)) / 0.45)
        if fin > 0:
            img = Image.blend(img, Image.new("RGBA", (W, H), (0, 0, 0, 255)), min(1, fin))
        return img.convert("RGB")

    _render(dest, W, H, dur, cuadro)


# ---------- placa de texto grande (pausas / datos / capítulos) ----------
def _retrato(ruta, lado):
    """Retrato cuadrado (cacheado), apenas desaturado para que pegue con la paleta."""
    clave = (str(ruta), int(lado))
    if clave not in _retrato.cache:
        from PIL import ImageEnhance
        im = Image.open(ruta).convert("RGB")
        w, h = im.size
        m = min(w, h)
        im = im.crop(((w - m) // 2, (h - m) // 2, (w - m) // 2 + m, (h - m) // 2 + m))
        im = ImageEnhance.Color(im).enhance(0.85).resize((int(lado), int(lado)), Image.LANCZOS)
        _retrato.cache[clave] = im
    return _retrato.cache[clave]


_retrato.cache = {}


def _circulo(im, borde=None, ancho=0):
    """Recorte circular RGBA, con aro opcional."""
    lado = im.size[0]
    sc = 4
    m = Image.new("L", (lado * sc, lado * sc), 0)
    ImageDraw.Draw(m).ellipse([0, 0, lado * sc - 1, lado * sc - 1], fill=255)
    m = m.resize((lado, lado), Image.LANCZOS)
    out = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    out.paste(im.convert("RGBA"), (0, 0), m)
    if borde and ancho:
        a = Image.new("RGBA", (lado * sc, lado * sc), (0, 0, 0, 0))
        ImageDraw.Draw(a).ellipse([0, 0, lado * sc - 1, lado * sc - 1], outline=borde, width=int(ancho * sc))
        out.alpha_composite(a.resize((lado, lado), Image.LANCZOS))
    return out


def placa(dest, W, H, dur, texto, sub="", etiqueta="", fondo=None, foto=None):
    """Título en mono que se escribe solo (las cifras en verde), etiqueta arriba y bajada en Plex.
    Alineada a la izquierda, sobre el partido desenfocado. foto = retrato de la persona nombrada (a la derecha)."""
    s = W / 1920
    T = texto.upper()
    tam = 150 if len(T) <= 9 else 120 if len(T) <= 14 else 96 if len(T) <= 22 else 78
    lado = 600 * s
    x = 96 * s
    ancho_txt = (W - 2 * x - lado - 80 * s) if foto else (W - 2 * x)
    f_t = fuente(700, tam * s)
    while foto and tam > 64 and max(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(p, font=f_t)
                                    for p in T.split()) > ancho_txt:
        tam -= 6
        f_t = fuente(700, tam * s)
    f_s = fuente(500, 42 * s, plex=True)
    f_e = fuente(500, 26 * s)
    esp_e = 4 * s
    lineas = _partir(T, f_t, ancho_txt)
    alto = tam * s * 1.04
    sub_l = _partir(sub, f_s, min(W * 0.7, ancho_txt)) if sub else []
    ret = _retrato(foto, lado) if foto else None
    xf, yf = W - x - lado, H / 2 - lado / 2 + 10 * s
    bloque = alto * len(lineas) + (60 * s + 52 * s * len(sub_l) if sub_l else 0)
    y0 = H / 2 - bloque / 2 + 10 * s
    total_letras = sum(len(l) for l in lineas)
    vel = min(0.035, 0.75 / max(1, total_letras))  # segundos por letra

    def cuadro(t, i, n):
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        a = ease(t / 0.35)
        _marca(d, s, int(255 * a))
        if ret is not None:  # el retrato entra desde la derecha detrás de un bloque verde, y se acerca apenas
            b = ease((t - 0.05) / 0.5)
            dx = (1 - b) * 120 * s
            d.rectangle([xf + 22 * s + dx, yf + 22 * s, xf + lado + 22 * s + dx, yf + lado + 22 * s],
                        fill=VERDE + (int(230 * b),))
            z = 1 + 0.05 * min(1.0, t / max(dur, 0.1))
            lz = int(lado * z)
            im = ret.resize((lz, lz), Image.BILINEAR)
            im = im.crop(((lz - int(lado)) // 2, (lz - int(lado)) // 2,
                          (lz - int(lado)) // 2 + int(lado), (lz - int(lado)) // 2 + int(lado))).convert("RGBA")
            im.putalpha(int(255 * b))
            capa.alpha_composite(im, (int(xf + dx), int(yf)))
            d.rectangle([xf + dx, yf, xf + lado + dx, yf + lado], outline=CLARO + (int(255 * b),),
                        width=max(2, int(4 * s)))
        if etiqueta:
            ye = y0 - 70 * s
            d.rectangle([x, ye + 6 * s, x + 46 * s * a, ye + 10 * s], fill=ACENTO + (int(255 * a),))
            _espaciado(d, (x + 62 * s, ye - 8 * s), etiqueta.upper(), f_e, ACENTO + (int(255 * a),), esp_e)
        k = int(max(0.0, t - 0.12) / vel)  # letras visibles
        resto, cursor = k, (x, y0)
        for li, l in enumerate(lineas):
            if resto <= 0:
                break
            yl = y0 + li * alto
            xx = x
            for c in l[:resto]:
                d.text((xx, yl), c, font=f_t, fill=(ACENTO if c.isdigit() else TEXTO) + (255,))
                xx += d.textlength(c, font=f_t)
            cursor = (xx, yl)
            resto -= len(l)
        escribiendo = k < total_letras
        if (escribiendo or int(t * 2.5) % 2 == 0) and t < 0.12 + vel * total_letras + 0.8:
            cx, cy = cursor
            d.rectangle([cx + 6 * s, cy + tam * s * 0.14, cx + 6 * s + tam * s * 0.14, cy + tam * s * 0.92],
                        fill=ACENTO + (255,))
        if sub_l:
            b = ease((t - 0.12 - vel * total_letras) / 0.4)
            ys = y0 + len(lineas) * alto + 34 * s + (1 - b) * 14 * s
            for m, l in enumerate(sub_l):
                d.text((x, ys + m * 52 * s), l, font=f_s, fill=CLARO + (int(255 * b),))
        return capa

    _render(dest, W, H, dur, cuadro, fondo)


# ---------- formación ----------
def formacion(dest, W, H, dur, jugadores, titulo="", etiqueta="", fondo=None):
    """Cancha vista desde arriba (ataca hacia la derecha) con un círculo vacío por puesto; cada jugador
    aparece con su retrato cuando el narrador lo nombra, y su nombre sale grande a la izquierda.
    jugadores = [{"nombre", "foto", "x", "y" (0-1 en la cancha; y=0 arriba = banda izquierda),
                  "puesto", "dato", "t" (segundos desde el inicio de la pieza; None = ya está desde el arranque)}]"""
    s = W / 1920
    # cancha a la derecha, proporción 105x68
    ch = 820 * s
    cw = ch * 105 / 68 * 0.84  # un poco más angosta para que entre (no es a escala exacta)
    cx0 = W - 70 * s - cw
    cy0 = (H - ch) / 2 + 30 * s
    r = 64 * s  # radio del retrato
    f_nom = fuente(700, 26 * s)
    f_big = fuente(700, 104 * s)
    f_pu = fuente(500, 40 * s, plex=True)
    f_e = fuente(500, 26 * s)
    f_ti = fuente(700, 44 * s)
    xl = 96 * s
    caras = {}
    for j in jugadores:
        if j.get("foto"):
            caras[j["nombre"]] = _circulo(_retrato(j["foto"], 2 * r))

    # la cancha (fija) se dibuja una sola vez
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    d.rectangle([cx0, cy0, cx0 + cw, cy0 + ch], fill=OSCURO + (150,))
    lc, lw = ACENTO + (120,), max(2, int(3 * s))
    d.rectangle([cx0, cy0, cx0 + cw, cy0 + ch], outline=lc, width=lw)
    d.line([cx0 + cw / 2, cy0, cx0 + cw / 2, cy0 + ch], fill=lc, width=lw)
    rc = ch * 9.15 / 68
    d.ellipse([cx0 + cw / 2 - rc, cy0 + ch / 2 - rc, cx0 + cw / 2 + rc, cy0 + ch / 2 + rc], outline=lc, width=lw)
    for lado in (0, 1):
        ah, aw = ch * 40.3 / 68, cw * 16.5 / 105
        x_a = cx0 if lado == 0 else cx0 + cw - aw
        d.rectangle([x_a, cy0 + (ch - ah) / 2, x_a + aw, cy0 + (ch + ah) / 2], outline=lc, width=lw)
        ah2, aw2 = ch * 18.3 / 68, cw * 5.5 / 105
        x_a = cx0 if lado == 0 else cx0 + cw - aw2
        d.rectangle([x_a, cy0 + (ch - ah2) / 2, x_a + aw2, cy0 + (ch + ah2) / 2], outline=lc, width=lw)

    def pos(j):
        return cx0 + j["x"] * cw, cy0 + j["y"] * ch

    def cuadro(t, i, n):
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        a = ease(t / 0.4)
        base_a = base.copy()
        if a < 1:
            base_a.putalpha(base_a.getchannel("A").point(lambda v: int(v * a)))
        capa.alpha_composite(base_a)
        d = ImageDraw.Draw(capa)
        _marca(d, s, int(255 * a))
        if etiqueta:
            d.rectangle([xl, 196 * s, xl + 46 * s * a, 200 * s], fill=ACENTO + (int(255 * a),))
            _espaciado(d, (xl + 62 * s, 182 * s), etiqueta.upper(), f_e, ACENTO + (int(255 * a),), 4 * s)
        if titulo:
            d.text((xl, 222 * s), titulo.upper(), font=f_ti, fill=TEXTO + (int(255 * a),))
        actual = None
        for j in jugadores:
            x, y = pos(j)
            tj = j.get("t")
            if tj is None or t >= tj:
                if tj is not None and (actual is None or tj >= actual.get("t", -1)):
                    actual = j
            # lugar vacío (punteado) hasta que lo nombran
            if tj is not None and t < tj + 0.1:
                for k in range(16):
                    ang0 = k * 22.5
                    d.arc([x - r, y - r, x + r, y + r], ang0, ang0 + 11, fill=ACENTO + (int(150 * a),),
                          width=max(2, int(3 * s)))
        for j in jugadores:
            x, y = pos(j)
            tj = j.get("t")
            p = 1.0 if tj is None else (t - tj) / 0.35
            if p <= 0:
                continue
            # pop: crece pasándose un poco y vuelve
            pe = min(1.0, p)
            esc = 1.0 if p >= 1 else (pe * 1.15 if pe < 0.7 else 1.15 - 0.15 * (pe - 0.7) / 0.3)
            esc = max(0.05, esc)
            destacado = j is actual and tj is not None
            rr = r * esc * (1.08 if destacado else 1.0)
            cara = caras.get(j["nombre"])
            aro = (ACENTO if destacado else CLARO)
            if cara is not None:
                c = cara.resize((max(2, int(2 * rr)), max(2, int(2 * rr))), Image.BILINEAR)
                capa.alpha_composite(c, (int(x - rr), int(y - rr)))
            else:
                d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=PANEL + (255,))
            d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=aro + (255,), width=max(3, int((7 if destacado else 4) * s)))
            if p >= 0.6:
                nom = j["nombre"].upper()
                tw = d.textlength(nom, font=f_nom)
                yy = y + rr + 8 * s
                d.rectangle([x - tw / 2 - 10 * s, yy, x + tw / 2 + 10 * s, yy + 36 * s],
                            fill=(ACENTO if destacado else CLARO) + (255,))
                d.text((x - tw / 2, yy + 3 * s), nom, font=f_nom, fill=OSCURO + (255,))
        # el nombrado, grande a la izquierda
        if actual is not None:
            b = ease((t - actual["t"]) / 0.3)
            yb = H / 2 - 40 * s
            nom = actual["nombre"].upper()
            d.text((xl - (1 - b) * 30 * s, yb), nom, font=f_big, fill=TEXTO + (int(255 * b),))
            linea = " · ".join(x for x in (actual.get("puesto"), actual.get("dato")) if x)
            if linea:
                d.rectangle([xl, yb + 140 * s, xl + 46 * s * b, yb + 144 * s], fill=ACENTO + (int(255 * b),))
                d.text((xl + 62 * s, yb + 120 * s), linea, font=f_pu, fill=CLARO + (int(255 * b),))
        return capa

    _render(dest, W, H, dur, cuadro, fondo)


# ---------- camino a la final ----------
def camino(dest, W, H, dur, partidos, titulo="", etiqueta="", fondo=None):
    """Llaves eliminadas, una fila por fase, que entra cuando el narrador nombra al rival.
    partidos = [{"fase", "rival", "color" [r,g,b], "ida", "vuelta", "global", "nota", "t" (seg desde el inicio)}]"""
    s = W / 1920
    xl = 96 * s
    f_e = fuente(500, 26 * s)
    f_ti = fuente(700, 44 * s)
    f_fase = fuente(600, 24 * s)
    f_riv = fuente(700, 70 * s)
    f_pq = fuente(500, 28 * s)
    f_gl = fuente(800, 84 * s)
    f_nota = fuente(500, 30 * s, plex=True)
    fila_h, gap = 190 * s, 34 * s
    n = len(partidos)
    y0 = max(310 * s, (H - (n * fila_h + (n - 1) * gap)) / 2 + 60 * s)
    x0, x1 = xl + 40 * s, W - xl

    def cuadro(t, i, nn):
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        a = ease(t / 0.35)
        _marca(d, s, int(255 * a))
        if etiqueta:
            d.rectangle([xl, 196 * s, xl + 46 * s * a, 200 * s], fill=ACENTO + (int(255 * a),))
            _espaciado(d, (xl + 62 * s, 182 * s), etiqueta.upper(), f_e, ACENTO + (int(255 * a),), 4 * s)
        if titulo:
            d.text((xl, 222 * s), titulo.upper(), font=f_ti, fill=TEXTO + (int(255 * a),))
        # línea del camino, crece hasta la última fila que ya entró
        visibles = [k for k, p in enumerate(partidos) if t >= p.get("t", 0)]
        if visibles:
            k = visibles[-1]
            p = partidos[k]
            b = ease((t - p.get("t", 0)) / 0.4)
            y_fin = y0 + fila_h / 2 + (k - 1 + b) * (fila_h + gap) if k else y0 + fila_h / 2 + 4 * s
            d.rectangle([xl + 10 * s, y0 + fila_h / 2 - 2 * s, xl + 14 * s, y_fin], fill=ACENTO + (200,))
        for k, p in enumerate(partidos):
            tp = p.get("t", 0)
            if t < tp:
                continue
            b = ease((t - tp) / 0.4)
            dx = (1 - b) * 80 * s
            al = int(255 * b)
            yt = y0 + k * (fila_h + gap)
            # punto en la línea
            d.ellipse([xl + 12 * s - 11 * s, yt + fila_h / 2 - 11 * s, xl + 12 * s + 11 * s, yt + fila_h / 2 + 11 * s],
                      fill=ACENTO + (al,))
            d.rectangle([x0 + dx, yt, x1 + dx, yt + fila_h], fill=OSCURO + (int(200 * b),))
            col = tuple(p.get("color", CLARO))
            d.rectangle([x0 + dx, yt, x0 + dx + 14 * s, yt + fila_h], fill=col + (al,))
            xx = x0 + dx + 50 * s
            _espaciado(d, (xx, yt + 30 * s), p["fase"].upper(), f_fase, ACENTO + (al,), 4 * s)
            d.text((xx, yt + 66 * s), p["rival"].upper(), font=f_riv, fill=TEXTO + (al,))
            # resultado global en caja clara, ida y vuelta al lado
            gl = p.get("global", "")
            gw = d.textlength(gl, font=f_gl) + 60 * s
            gx = x1 + dx - gw - 30 * s
            b2 = ease((t - tp - 0.25) / 0.35)
            if b2 > 0:
                d.rectangle([gx, yt + 30 * s, gx + gw, yt + fila_h - 30 * s], fill=CLARO + (int(255 * b2),))
                d.text((gx + 30 * s, yt + 44 * s), gl, font=f_gl, fill=OSCURO + (int(255 * b2),))
                lin = []
                if p.get("ida"):
                    lin.append(f"IDA {p['ida']}")
                if p.get("vuelta"):
                    lin.append(f"VUELTA {p['vuelta']}")
                txt = "  ·  ".join(lin)
                tw = d.textlength(txt, font=f_pq)
                d.text((gx - 40 * s - tw, yt + 52 * s), txt, font=f_pq, fill=CLARO + (int(255 * b2),))
                if p.get("nota"):
                    nw = d.textlength(p["nota"], font=f_nota)
                    d.text((gx - 40 * s - nw, yt + 102 * s), p["nota"], font=f_nota, fill=ACENTO + (int(255 * b2),))
        return capa

    _render(dest, W, H, dur, cuadro, fondo)


# ---------- tabla de posiciones ----------
def tabla(dest, W, H, dur, equipos, titulo="", etiqueta="", destacar="", zona=0, zona_texto="",
          t_destacar=None, t_zona=None, t_diferencia=None, fondo=None, nota="", t_nota=None):
    """Tabla animada: las filas entran, las barras de puntos crecen con los números contando, después se
    destaca un equipo (t_destacar), aparece la línea de los puestos de copa debajo del puesto `zona` (t_zona)
    y la distancia en puntos entre el destacado y el primero (t_diferencia).
    equipos = [{"nombre", "puntos", "color" [r,g,b]}] en orden."""
    s = W / 1920
    xl = 96 * s
    f_e = fuente(500, 26 * s)
    f_ti = fuente(700, 44 * s)
    f_pos = fuente(700, 40 * s)
    f_eq = fuente(700, 40 * s)
    f_pt = fuente(800, 42 * s)
    f_dif = fuente(800, 52 * s)
    f_dt = fuente(600, 24 * s)
    f_z = fuente(600, 22 * s)
    n = len(equipos)
    fila_h, gap = 84 * s, 14 * s
    y0 = 300 * s
    x_pos, x_eq = xl, xl + 80 * s
    x_bar = xl + 560 * s
    bar_max = W - xl - (430 * s if destacar else 160 * s) - x_bar  # lugar a la derecha para "−37 ..."
    pmax = max(e["puntos"] for e in equipos)
    ifo = next((k for k, e in enumerate(equipos) if e["nombre"] == destacar), None)

    def yfila(k):
        return y0 + k * (fila_h + gap)

    def cuadro(t, i, nn):
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        a = ease(t / 0.35)
        _marca(d, s, int(255 * a))
        if etiqueta:
            d.rectangle([xl, 196 * s, xl + 46 * s * a, 200 * s], fill=ACENTO + (int(255 * a),))
            _espaciado(d, (xl + 62 * s, 182 * s), etiqueta.upper(), f_e, ACENTO + (int(255 * a),), 4 * s)
        if titulo:
            d.text((xl, 222 * s), titulo.upper(), font=f_ti, fill=TEXTO + (int(255 * a),))
        hd = 0.0 if t_destacar is None else ease((t - t_destacar) / 0.4)
        crece = ease((t - 0.5) / 1.4)  # todas las barras crecen juntas
        for k, e in enumerate(equipos):
            tk = 0.2 + 0.07 * k
            b = ease((t - tk) / 0.35)
            if b <= 0:
                continue
            al = int(255 * b)
            y = yfila(k) + (1 - b) * 20 * s
            es_dest = k == ifo
            apagado = 1 - 0.55 * hd if not es_dest else 1.0
            fondo_fila = (PANEL if es_dest and hd > 0 else OSCURO)
            d.rectangle([xl - 20 * s, y, W - xl + 20 * s, y + fila_h], fill=fondo_fila + (int(170 * b),))
            if es_dest and hd > 0:
                d.rectangle([xl - 20 * s, y, xl - 8 * s, y + fila_h], fill=ACENTO + (int(255 * hd),))
            col_t = tuple(int(c * apagado) for c in TEXTO)
            d.text((x_pos, y + 18 * s), f"{k + 1}", font=f_pos, fill=(ACENTO if es_dest and hd > 0 else col_t) + (al,))
            d.rectangle([x_eq, y + 22 * s, x_eq + 12 * s, y + fila_h - 22 * s], fill=tuple(e.get("color", CLARO)) + (al,))
            d.text((x_eq + 34 * s, y + 18 * s), e["nombre"].upper(), font=f_eq, fill=col_t + (al,))
            # barra de puntos
            pts = e["puntos"] * crece
            wb = bar_max * pts / pmax
            col_b = tuple(e.get("color", CLARO)) if es_dest else VERDE
            col_b = tuple(int(c * apagado) for c in col_b)
            if wb > 1:
                d.rectangle([x_bar, y + 20 * s, x_bar + wb, y + fila_h - 20 * s], fill=col_b + (al,))
            d.text((x_bar + wb + 16 * s, y + 16 * s), f"{int(round(pts))}", font=f_pt, fill=col_t + (al,))
        # línea de los puestos de Champions
        if zona and t_zona is not None and t >= t_zona:
            bz = ease((t - t_zona) / 0.45)
            yz = yfila(zona) - gap / 2
            xx = xl - 20 * s
            while xx < xl - 20 * s + (W - 2 * xl + 40 * s) * bz:
                d.rectangle([xx, yz - 2 * s, xx + 18 * s, yz + 2 * s], fill=CLARO + (255,))
                xx += 30 * s
            if zona_texto:
                tw = _ancho_esp(zona_texto.upper(), f_z, 3 * s)
                d.rectangle([W - xl - tw - 16 * s, yz - 44 * s, W - xl + 8 * s, yz - 6 * s], fill=CLARO + (int(255 * bz),))
                _espaciado(d, (W - xl - tw - 4 * s, yz - 38 * s), zona_texto.upper(), f_z, OSCURO + (int(255 * bz),), 3 * s)
        if nota and t_nota is not None and t >= t_nota:  # cartel abajo de la tabla
            bn = ease((t - t_nota) / 0.35)
            yn = yfila(n) + 20 * s + (1 - bn) * 20 * s
            f_n = fuente(700, 46 * s)
            tw = d.textlength(nota.upper(), font=f_n)
            d.rectangle([xl - 20 * s, yn, xl + tw + 30 * s, yn + 76 * s], fill=CLARO + (int(255 * bn),))
            d.text((xl + 5 * s, yn + 14 * s), nota.upper(), font=f_n, fill=OSCURO + (int(255 * bn),))
        # diferencia con el primero
        if ifo is not None and t_diferencia is not None and t >= t_diferencia:
            bd = ease((t - t_diferencia) / 0.5)
            x_a = x_bar + bar_max * equipos[ifo]["puntos"] / pmax
            x_b = x_bar + bar_max
            yl = yfila(ifo) + fila_h / 2
            # guía punteada desde el primero hasta la fila destacada
            yy = yfila(0) + fila_h - 20 * s
            while yy < yfila(0) + fila_h + (yl - yfila(0) - fila_h) * bd:
                d.rectangle([x_b - 2 * s, yy, x_b + 2 * s, yy + 12 * s], fill=CLARO + (220,))
                yy += 22 * s
            # "barra fantasma" con los puntos que le faltaron, y la diferencia a la derecha
            yf = yfila(ifo)
            xe = x_a + (x_b - x_a) * bd
            if xe > x_a + 2:
                d.rectangle([x_a, yf + 20 * s, xe, yf + fila_h - 20 * s], fill=ACENTO + (int(60 * bd),),
                            outline=CLARO + (255,), width=max(2, int(3 * s)))
            d.text((x_a + 16 * s, yf + 16 * s), str(equipos[ifo]["puntos"]), font=f_pt, fill=TEXTO + (255,))
            dif = int(round((equipos[0]["puntos"] - equipos[ifo]["puntos"]) * bd))
            txt = f"−{dif}"
            xt = x_b + 28 * s
            d.text((xt, yf + 12 * s), txt, font=f_dif, fill=TEXTO + (int(255 * bd),))
            xt2 = xt + d.textlength(txt, font=f_dif) + 14 * s
            d.text((xt2, yf + 16 * s), "PUNTOS", font=f_dt, fill=CLARO + (int(255 * bd),))
            d.text((xt2, yf + 44 * s), "DEL CAMPEÓN", font=f_dt, fill=CLARO + (int(255 * bd),))
        return capa

    _render(dest, W, H, dur, cuadro, fondo)


# ---------- palmarés ----------
def _copa(d, cx, base_y, h, color):
    """Copa de Europa estilizada (orejona): copa, dos asas grandes, pie y base. base_y = abajo de todo."""
    w = h * 0.5
    top = base_y - h
    lw = max(2, int(h * 0.07))
    # asas
    d.ellipse([cx - w * 1.05, top + h * 0.05, cx - w * 0.25, top + h * 0.62], outline=color, width=lw)
    d.ellipse([cx + w * 0.25, top + h * 0.05, cx + w * 1.05, top + h * 0.62], outline=color, width=lw)
    # copa
    d.chord([cx - w * 0.55, top - h * 0.25, cx + w * 0.55, top + h * 0.62], 0, 180, fill=color)
    d.rectangle([cx - w * 0.55, top, cx + w * 0.55, top + h * 0.19], fill=color)
    # pie y base
    d.polygon([(cx - w * 0.1, top + h * 0.6), (cx + w * 0.1, top + h * 0.6), (cx + w * 0.2, top + h * 0.85),
               (cx - w * 0.2, top + h * 0.85)], fill=color)
    d.rectangle([cx - w * 0.42, top + h * 0.85, cx + w * 0.42, base_y], fill=color)


def palmares(dest, W, H, dur, titulos, texto="", etiqueta="", desde=None, hasta=None, fondo=None):
    """Línea de tiempo con una copa por título: cada una aparece (en su "t") con su final abajo
    (rival, resultado, sede), y el contador grande de arriba va sumando.
    titulos = [{"año", "rival", "resultado", "sede", "t"}]"""
    s = W / 1920
    xl = 96 * s
    f_e = fuente(500, 26 * s)
    f_num = fuente(800, 150 * s)
    f_tx = fuente(700, 64 * s)
    f_an = fuente(700, 40 * s)
    f_tick = fuente(500, 22 * s)
    f_riv = fuente(600, 24 * s)
    f_res = fuente(800, 40 * s)
    f_sede = fuente(500, 24 * s, plex=True)
    años = [x["año"] for x in titulos]
    a0 = desde or min(años) - 1
    a1 = hasta or max(años) + 1
    xa, xb = xl + 60 * s, W - xl - 60 * s
    yl = 660 * s

    def xaño(a):
        return xa + (xb - xa) * (a - a0) / (a1 - a0)

    def cuadro(t, i, nn):
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        a = ease(t / 0.35)
        _marca(d, s, int(255 * a))
        if etiqueta:
            d.rectangle([xl, 196 * s, xl + 46 * s * a, 200 * s], fill=ACENTO + (int(255 * a),))
            _espaciado(d, (xl + 62 * s, 182 * s), etiqueta.upper(), f_e, ACENTO + (int(255 * a),), 4 * s)
        cuantos = sum(1 for x in titulos if t >= x["t"])
        d.text((xl, 222 * s), str(cuantos), font=f_num, fill=ACENTO + (int(255 * a),))
        if texto:
            d.text((xl + d.textlength(str(cuantos), font=f_num) + 30 * s, 268 * s), texto.upper(), font=f_tx,
                   fill=TEXTO + (int(255 * a),))
        # la línea se dibuja de izquierda a derecha
        bl = ease((t - 0.1) / 0.8)
        d.rectangle([xa, yl - 2 * s, xa + (xb - xa) * bl, yl + 2 * s], fill=CLARO + (160,))
        for año in range(a0, a1 + 1):
            x = xaño(año)
            if x > xa + (xb - xa) * bl:
                continue
            gana = año in años
            d.rectangle([x - 1.5 * s, yl - 10 * s, x + 1.5 * s, yl + 10 * s], fill=CLARO + (160,))
            if not gana:
                tw = d.textlength(str(año), font=f_tick)
                d.text((x - tw / 2, yl + 20 * s), str(año), font=f_tick, fill=CLARO + (130,))
        for x_ in titulos:
            tp = x_["t"]
            if t < tp:
                continue
            b = min(1.0, (t - tp) / 0.35)
            esc = b * 1.18 if b < 0.7 else 1.18 - 0.18 * (b - 0.7) / 0.3
            x = xaño(x_["año"])
            al = int(255 * min(1, b * 1.5))
            # destello
            if t - tp < 0.5:
                r = 40 * s + (t - tp) * 260 * s
                d.ellipse([x - r, yl - 120 * s - r, x + r, yl - 120 * s + r], outline=ACENTO + (int(200 * (1 - (t - tp) / 0.5)),),
                          width=max(2, int(4 * s)))
            _copa(d, x, yl - 26 * s, 140 * s * esc, CLARO + (al,))
            d.ellipse([x - 9 * s, yl - 9 * s, x + 9 * s, yl + 9 * s], fill=ACENTO + (al,))
            # ficha de la final
            b2 = ease((t - tp - 0.15) / 0.35)
            if b2 > 0:
                yc = yl + 34 * s + (1 - b2) * 20 * s
                an = str(x_["año"])
                tw = d.textlength(an, font=f_an)
                d.text((x - tw / 2, yc), an, font=f_an, fill=ACENTO + (int(255 * b2),))
                for k, (txt, f, col) in enumerate([(x_.get("rival", "").upper(), f_riv, TEXTO),
                                                    (x_.get("resultado", ""), f_res, CLARO),
                                                    (x_.get("sede", ""), f_sede, ACENTO)]):
                    if not txt:
                        continue
                    yy = yc + [56, 92, 146][k] * s
                    tw = d.textlength(txt, font=f)
                    d.text((x - tw / 2, yy), txt, font=f, fill=col + (int(255 * b2),))
        return capa

    _render(dest, W, H, dur, cuadro, fondo)


# ---------- línea de tiempo con tramos ----------
def linea_tiempo(dest, W, H, dur, desde, hasta, tramos, contador=None, etiqueta="", fondo=None):
    """Eje de años; cada tramo es una barra que se estira de "desde" a "hasta" en su "t", con su texto.
    contador = {"desde", "hasta", "texto", "t", "fin_texto"}: barra final que recorre los años contando."""
    s = W / 1920
    xl = 96 * s
    f_e = fuente(500, 26 * s)
    f_tick = fuente(500, 22 * s)
    f_tr = fuente(700, 34 * s)
    f_num = fuente(800, 150 * s)
    f_ct = fuente(700, 56 * s)
    f_fin = fuente(600, 26 * s)
    xa, xb = xl + 20 * s, W - xl - 20 * s
    ye = 820 * s

    def xaño(a):
        return xa + (xb - xa) * (a - desde) / (hasta - desde)

    def cuadro(t, i, nn):
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        a = ease(t / 0.35)
        _marca(d, s, int(255 * a))
        if etiqueta:
            d.rectangle([xl, 196 * s, xl + 46 * s * a, 200 * s], fill=ACENTO + (int(255 * a),))
            _espaciado(d, (xl + 62 * s, 182 * s), etiqueta.upper(), f_e, ACENTO + (int(255 * a),), 4 * s)
        bl = ease(t / 0.7)
        d.rectangle([xa, ye - 2 * s, xa + (xb - xa) * bl, ye + 2 * s], fill=CLARO + (170,))
        for año in range(desde, hasta + 1):
            x = xaño(año)
            if x > xa + (xb - xa) * bl:
                break
            largo = 14 if año % 5 == 0 else 7
            d.rectangle([x - 1.5 * s, ye - largo * s, x + 1.5 * s, ye + largo * s], fill=CLARO + (170,))
            if año % 5 == 0 or año in (desde, hasta):
                tw = d.textlength(str(año), font=f_tick)
                d.text((x - tw / 2, ye + 22 * s), str(año), font=f_tick, fill=CLARO + (200,))
        for k, tr in enumerate(tramos):
            if t < tr["t"]:
                continue
            b = ease((t - tr["t"]) / 0.6)
            y = ye - (110 + 90 * k) * s
            x0, x1 = xaño(tr["desde"]), xaño(tr["desde"] + (tr["hasta"] - tr["desde"]) * b)
            col = tuple(tr.get("color", VERDE))
            d.rectangle([x0, y, x1, y + 50 * s], fill=col + (235,))
            d.text((x1 + 18 * s, y + 6 * s), tr["texto"].upper(), font=f_tr, fill=TEXTO + (int(255 * min(1, b * 2)),))
        if contador and t >= contador["t"]:
            c = contador
            b = ease((t - c["t"]) / 1.6)
            y = ye - (110 + 90 * len(tramos)) * s - 30 * s
            x0, x1 = xaño(c["desde"]), xaño(c["desde"] + (c["hasta"] - c["desde"]) * b)
            d.rectangle([x0, y, x1, y + 14 * s], fill=ACENTO + (255,))
            d.ellipse([x1 - 14 * s, y - 7 * s, x1 + 14 * s, y + 21 * s], fill=ACENTO + (255,))
            n = int(round((c["hasta"] - c["desde"]) * b))
            d.text((xl, 250 * s), str(n), font=f_num, fill=ACENTO + (255,))
            d.text((xl + d.textlength(str(n), font=f_num) + 30 * s, 300 * s), c["texto"].upper(), font=f_ct,
                   fill=TEXTO + (255,))
            if b >= 1 and c.get("fin_texto"):
                b3 = ease((t - c["t"] - 1.6) / 0.3)
                tw = d.textlength(c["fin_texto"].upper(), font=f_fin)
                d.rectangle([x1 - tw - 30 * s, y - 60 * s, x1 + 10 * s, y - 18 * s], fill=CLARO + (int(255 * b3),))
                d.text((x1 - tw - 10 * s, y - 54 * s), c["fin_texto"].upper(), font=f_fin, fill=OSCURO + (int(255 * b3),))
        return capa

    _render(dest, W, H, dur, cuadro, fondo)


# ---------- capítulo ----------
def capitulo(dest, W, H, dur, numero, titulo, total=0, fondo=None):
    """Separador de capítulo: número grande calado, título que se escribe, y una fila de marcas con los
    capítulos (el actual en verde) para que se entienda en qué parte de la historia estamos."""
    s = W / 1920
    xl = 96 * s
    f_num = fuente(800, 330 * s)
    f_cap = fuente(600, 30 * s)
    f_ti = fuente(700, 110 * s)
    T = titulo.upper()
    num = f"{numero:02d}"

    def cuadro(t, i, nn):
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        a = ease(t / 0.3)
        out = min(1.0, max(0.0, (dur - t) / 0.3))
        al = a * out
        _marca(d, s, int(255 * al))
        # número calado, entra deslizando
        xn = xl - (1 - ease(t / 0.5)) * 60 * s
        d.text((xn, 250 * s), num, font=f_num, fill=(0, 0, 0, 0), stroke_width=max(2, int(4 * s)),
               stroke_fill=ACENTO + (int(230 * al),))
        _espaciado(d, (xl, 640 * s), f"CAPÍTULO {numero}", f_cap, ACENTO + (int(255 * al),), 6 * s)
        k = int(max(0.0, t - 0.25) / 0.035)
        d.text((xl, 690 * s), T[:k], font=f_ti, fill=TEXTO + (int(255 * out),))
        wl = (W - 2 * xl) * ease((t - 0.2) / 0.6)
        d.rectangle([xl, 830 * s, xl + wl, 834 * s], fill=CLARO + (int(150 * al),))
        if total:
            for c in range(1, total + 1):
                x = xl + (c - 1) * 70 * s
                col = ACENTO if c == numero else (CLARO if c < numero else VERDE)
                h = 16 * s if c == numero else 8 * s
                d.rectangle([x, 870 * s, x + 54 * s, 870 * s + h], fill=col + (int(255 * al),))
        return capa

    _render(dest, W, H, dur, cuadro, fondo)


# ---------- cambio ----------
def cambio(dest, W, H, dur, sale, entra, minuto="", etiqueta="", fondo=None):
    """Cambio de jugadores: sale = {"nombre", "foto", "texto"}, entra = ídem. Los retratos entran desde los
    costados, flecha roja abajo (sale) y verde arriba (entra), y el minuto en el medio."""
    s = W / 1920
    r = 190 * s
    f_e = fuente(500, 26 * s)
    f_lab = fuente(600, 28 * s)
    f_nom = fuente(700, 64 * s)
    f_tx = fuente(500, 34 * s, plex=True)
    f_min = fuente(800, 120 * s)
    xl = 96 * s
    lados = [(sale, W * 0.27, (200, 40, 40), "SALE", -1), (entra, W * 0.73, ACENTO, "ENTRA", 1)]
    caras = {id(j): _circulo(_retrato(j["foto"], 2 * r)) if j.get("foto") else None for j, *_ in lados}

    def cuadro(t, i, nn):
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        a = ease(t / 0.35)
        _marca(d, s, int(255 * a))
        if etiqueta:
            d.rectangle([xl, 196 * s, xl + 46 * s * a, 200 * s], fill=ACENTO + (int(255 * a),))
            _espaciado(d, (xl + 62 * s, 182 * s), etiqueta.upper(), f_e, ACENTO + (int(255 * a),), 4 * s)
        for k, (j, cx, col, lab, dirr) in enumerate(lados):
            tk = 0.15 + 0.35 * k
            b = ease((t - tk) / 0.45)
            if b <= 0:
                continue
            x = cx + dirr * (1 - b) * 200 * s
            cy = H * 0.5
            cara = caras[id(j)]
            if cara is not None:
                c = cara.copy()
                if lab == "SALE":  # el que sale, apagado
                    from PIL import ImageEnhance
                    c = ImageEnhance.Brightness(c).enhance(0.7)
                c.putalpha(c.getchannel("A").point(lambda v: int(v * b)))
                capa.alpha_composite(c, (int(x - r), int(cy - r)))
            d.ellipse([x - r, cy - r, x + r, cy + r], outline=col + (int(255 * b),), width=max(4, int(8 * s)))
            # flecha
            ya = cy - r - 70 * s
            fl = 26 * s
            if dirr > 0:
                d.polygon([(x, ya - fl), (x - fl, ya + fl * 0.4), (x + fl, ya + fl * 0.4)], fill=col + (int(255 * b),))
            else:
                d.polygon([(x, ya + fl), (x - fl, ya - fl * 0.4), (x + fl, ya - fl * 0.4)], fill=col + (int(255 * b),))
            tw = _ancho_esp(lab, f_lab, 5 * s)
            _espaciado(d, (x - tw / 2, ya - 70 * s), lab, f_lab, col + (int(255 * b),), 5 * s)
            nom = j["nombre"].upper()
            tw = d.textlength(nom, font=f_nom)
            d.text((x - tw / 2, cy + r + 24 * s), nom, font=f_nom, fill=TEXTO + (int(255 * b),))
            if j.get("texto"):
                tw = d.textlength(j["texto"], font=f_tx)
                d.text((x - tw / 2, cy + r + 104 * s), j["texto"], font=f_tx, fill=CLARO + (int(255 * b),))
        if minuto:
            b = ease((t - 0.6) / 0.35)
            tw = d.textlength(minuto, font=f_min)
            d.text((W / 2 - tw / 2, H * 0.5 - 70 * s), minuto, font=f_min, fill=TEXTO + (int(255 * b),))
            # flechas de intercambio
            d.line([W / 2 - 120 * s, H * 0.5 + 90 * s, W / 2 + 120 * s, H * 0.5 + 90 * s], fill=ACENTO + (int(255 * b),),
                   width=max(2, int(4 * s)))
        return capa

    _render(dest, W, H, dur, cuadro, fondo)


# ---------- marcador ----------
def marcador(dest, W, H, dur, local, visitante, goles, etiqueta="", cambios=None, fondo=None):
    """goles=(gl, gv). cambios=[[seg, gl, gv, 'texto opcional'], ...] anima los goles.
    Tres cajas: equipo (con su color abajo) | resultado (claro) | equipo."""
    s = W / 1920
    f_eq = fuente(700, 76 * s)
    f_gol = fuente(800, 132 * s)
    f_e = fuente(500, 26 * s)
    f_n = fuente(700, 34 * s)
    esp_e = 4 * s
    eventos = sorted(cambios or [], key=lambda c: c[0])
    L, V = local.upper(), visitante.upper()
    d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    pad = 44 * s
    wl = d0.textlength(L, font=f_eq) + 2 * pad
    wv = d0.textlength(V, font=f_eq) + 2 * pad
    wg = d0.textlength("0 - 0", font=f_gol) + 2 * pad
    hb = 190 * s
    xg = W / 2 - wg / 2
    yb = H / 2 - hb / 2

    def estado(t):
        gl, gv, nota, t_cambio = goles[0], goles[1], "", -10
        for c in eventos:
            if t >= c[0]:
                gl, gv, t_cambio = c[1], c[2], c[0]
                nota = c[3] if len(c) > 3 else ""
        return gl, gv, nota, t_cambio

    def cuadro(t, i, n):
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        a = ease(t / 0.45)
        al = int(255 * a)
        _marca(d, s, al)
        gl, gv, nota, tc = estado(t)
        if etiqueta:
            w = _ancho_esp(etiqueta.upper(), f_e, esp_e)
            _espaciado(d, (W / 2 - w / 2, yb - 70 * s), etiqueta.upper(), f_e, ACENTO + (al,), esp_e)
        off = (1 - a) * 120 * s
        # equipo local
        x1 = xg - wl - off
        d.rectangle([x1, yb, x1 + wl, yb + hb], fill=PANEL + (int(235 * a),))
        d.rectangle([x1, yb + hb - 10 * s, x1 + wl, yb + hb], fill=COLOR_EQUIPO.get(L, ACENTO) + (al,))
        d.text((x1 + pad, yb + hb / 2 - 50 * s), L, font=f_eq, fill=TEXTO + (al,))
        # equipo visitante
        x2 = xg + wg + off
        d.rectangle([x2, yb, x2 + wv, yb + hb], fill=PANEL + (int(235 * a),))
        d.rectangle([x2, yb + hb - 10 * s, x2 + wv, yb + hb], fill=COLOR_EQUIPO.get(V, ACENTO) + (al,))
        d.text((x2 + pad, yb + hb / 2 - 50 * s), V, font=f_eq, fill=TEXTO + (al,))
        # resultado (se pone verde un instante cuando cambia)
        pulso = max(0.0, 1 - (t - tc) / 0.7) if t >= tc else 0
        caja = tuple(int(TEXTO[k] + (ACENTO[k] - TEXTO[k]) * pulso) for k in range(3))
        d.rectangle([xg, yb, xg + wg, yb + hb], fill=caja + (al,))
        txt = f"{gl} - {gv}"
        sube = (1 - ease((t - tc) / 0.25)) * 30 * s if t >= tc and tc >= 0 else 0
        d.text((W / 2 - d.textlength(txt, font=f_gol) / 2, yb + hb / 2 - 88 * s + sube), txt,
               font=f_gol, fill=FONDO + (al,))
        if nota:
            b = ease((t - tc) / 0.35)
            w = d.textlength(nota, font=f_n) + 40 * s
            yn = yb + hb + 40 * s
            d.rectangle([W / 2 - w / 2, yn, W / 2 + w / 2, yn + 62 * s], fill=CLARO + (int(255 * b),))
            d.text((W / 2 - w / 2 + 20 * s, yn + 12 * s), nota, font=f_n, fill=FONDO + (int(255 * b),))
        return capa

    _render(dest, W, H, dur, cuadro, fondo)


# ---------- jugada: la cancha en perspectiva con el recorrido de la pelota (pedido del usuario, 11/11) ----------
def _homografia(src, dst):
    """Matriz 3x3 que lleva los 4 puntos src a los 4 dst."""
    import numpy as np
    A, b = [], []
    for (x, y), (u, v) in zip(src, dst):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); b.append(v)
    h = np.linalg.solve(np.array(A, float), np.array(b, float))
    return np.append(h, 1.0).reshape(3, 3)


def _interp(puntos, t):
    """Posición (x, y) en el segundo t sobre una lista de puntos {"x", "y", "t"} (lineal entre puntos)."""
    if t <= puntos[0]["t"]:
        return puntos[0]["x"], puntos[0]["y"], 0
    for k in range(1, len(puntos)):
        a, b = puntos[k - 1], puntos[k]
        if t <= b["t"]:
            u = (t - a["t"]) / max(1e-6, b["t"] - a["t"])
            if b.get("suave"):
                u = u * u * (3 - 2 * u)
            return a["x"] + (b["x"] - a["x"]) * u, a["y"] + (b["y"] - a["y"]) * u, k
    return puntos[-1]["x"], puntos[-1]["y"], len(puntos) - 1


def _textura_cancha(K):
    """La cancha completa (105x68 m) dibujada a K px por metro, con franjas de corte de pasto."""
    import numpy as np
    M = int(4 * K)  # margen de 4 m alrededor (para los arcos)
    PW, PH = int(105 * K), int(68 * K)
    img = Image.new("RGBA", (PW + 2 * M, PH + 2 * M), (38, 62, 38, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([M, M, M + PW, M + PH], fill=PANEL + (255,))
    for k in range(0, 105, 10):  # franjas
        if (k // 10) % 2:
            d.rectangle([M + k * K, M, M + (k + 10) * K, M + PH], fill=(50, 82, 50, 255))
    lc, lw = CLARO + (210,), max(2, int(K * 0.16))
    for lado in (0, 1):  # arcos (7,32 x 2,44 m)
        gx0, gx1 = (M - 2.44 * K, M) if lado == 0 else (M + PW, M + PW + 2.44 * K)
        d.rectangle([gx0, M + PH / 2 - 3.66 * K, gx1, M + PH / 2 + 3.66 * K], fill=(230, 230, 230, 60), outline=lc, width=lw)
    img2 = img.crop((M, M, M + PW, M + PH))
    d2 = ImageDraw.Draw(img2)
    d, img_full = d2, img
    d.rectangle([lw // 2, lw // 2, PW - lw // 2, PH - lw // 2], outline=lc, width=lw)
    d.line([PW / 2, 0, PW / 2, PH], fill=lc, width=lw)
    rc = 9.15 * K
    d.ellipse([PW / 2 - rc, PH / 2 - rc, PW / 2 + rc, PH / 2 + rc], outline=lc, width=lw)
    d.ellipse([PW / 2 - lw, PH / 2 - lw, PW / 2 + lw, PH / 2 + lw], fill=lc)
    for lado in (0, 1):
        ah, aw = 40.3 * K, 16.5 * K
        x_a = 0 if lado == 0 else PW - aw
        d.rectangle([x_a, (PH - ah) / 2, x_a + aw, (PH + ah) / 2], outline=lc, width=lw)
        ah2, aw2 = 18.3 * K, 5.5 * K
        x_a = 0 if lado == 0 else PW - aw2
        d.rectangle([x_a, (PH - ah2) / 2, x_a + aw2, (PH + ah2) / 2], outline=lc, width=lw)
        px = 11 * K if lado == 0 else PW - 11 * K
        d.ellipse([px - lw, PH / 2 - lw, px + lw, PH / 2 + lw], fill=lc)
    img_full.paste(img2, (M, M))
    return img_full


def jugada(dest, W, H, dur, pelota, jugadores=(), titulo="", etiqueta="", minuto="", datos=(), contador=None,
           ancho=62.0, color_rival=(236, 236, 236), color_arg=(117, 170, 219), fondo=None, seguir=True):
    """Cancha vista en perspectiva (ataca hacia la derecha) con la pelota recorriendo la jugada: estela
    verde, rivales que se apagan cuando los deja atrás, retratos de los protagonistas y contador de metros/segundos.
    pelota = [{"x", "y", "t"}] en METROS de cancha (x 0-105, y 0-68; y=0 banda de arriba), t en segundos de la pieza;
             {"aire": true} en el punto de llegada = pelota por el aire (traza punteada).
    jugadores = [{"nombre", "equipo": "arg"|"rival", "x", "y", "foto", "mov": [{"x","y","t"}], "vencido": t, "etiqueta"}]
    datos = [{"a": "60 METROS", "b": "10,8 SEGUNDOS", "t": [t0, t1]}]   contador = {"desde": t0, "hasta": t1}
    ancho = metros de cancha visibles (la cámara sigue a la pelota)."""
    import math
    import numpy as np
    s = W / 1920
    K = 16
    tex = _textura_cancha(K)
    f_e = fuente(500, 26 * s)
    f_ti = fuente(700, 44 * s)
    f_nom = fuente(700, 22 * s)
    f_et = fuente(600, 18 * s)
    f_min = fuente(700, 230 * s)
    f_cont = fuente(700, 64 * s)
    f_cl = fuente(500, 22 * s)
    f_da = fuente(700, 92 * s)
    f_db = fuente(700, 30 * s)
    xl = 96 * s
    caras = {}
    for j in jugadores:
        if j.get("foto"):
            caras[j["nombre"]] = _circulo(_retrato(j["foto"], int(76 * s)))
    pel = sorted(pelota, key=lambda p: p["t"])
    t_ini, t_fin = pel[0]["t"], pel[-1]["t"]
    # largo del recorrido (para el contador) y muestreo de la estela
    def largo_hasta(t):
        L, prev = 0.0, None
        tt = pel[0]["t"]
        while tt < min(t, t_fin) + 1e-9:
            x, y, _ = _interp(pel, tt)
            if prev:
                L += math.hypot(x - prev[0], y - prev[1])
            prev = (x, y)
            tt += 0.05
        return L

    def jug_pos(j, t):
        if j.get("mov"):
            pts = [{"x": j["x"], "y": j["y"], "t": j["mov"][0]["t"] - 1e-3}] + list(j["mov"])
            x, y, _ = _interp(pts, t)
            return x, y
        return j["x"], j["y"]

    def cuadro(t, i, n):
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        a = ease(t / 0.5)
        # cámara: ventana de `ancho` metros centrada en la pelota (con un poco de retraso)
        bx, by, _ = _interp(pel, t - 0.2)
        if not seguir:
            bx = 52.5
        ww = min(105.0, ancho)
        wx0 = max(0.0, min(105.0 - ww, bx - ww / 2))
        # entrada: de vista cenital a perspectiva
        incl = 0.56 + 0.44 * (1 - ease(t / 0.9))
        y0, y1 = H * 0.27, H * 1.0
        x0, x1 = -W * 0.06, W * 1.06
        cx = W / 2
        top_w = (x1 - x0) * incl
        quad_dst = [(cx - top_w / 2, y0), (cx + top_w / 2, y0), (x1, y1), (x0, y1)]
        quad_src = [(wx0, 0.0), (wx0 + ww, 0.0), (wx0 + ww, 68.0), (wx0, 68.0)]
        Hm = _homografia(quad_src, quad_dst)  # metros -> pantalla
        Hinv = np.linalg.inv(_homografia([((x + 4) * K, (y + 4) * K) for x, y in quad_src], quad_dst))  # pantalla -> textura
        coef = (Hinv / Hinv[2, 2]).flatten()[:8]
        cancha = tex.transform((W, H), Image.PERSPECTIVE, tuple(coef), Image.BILINEAR)
        if a < 1:
            cancha.putalpha(cancha.getchannel("A").point(lambda v: int(v * a)))
        capa.alpha_composite(cancha)
        # sombra/viñeta abajo para que el texto se lea
        d = ImageDraw.Draw(capa)

        def P(x, y):
            p = Hm @ (x, y, 1.0)
            return p[0] / p[2], p[1] / p[2]

        # estela de la pelota
        if t > t_ini:
            pts, tt = [], t_ini
            fin = min(t, t_fin)
            while tt <= fin:
                x, y, k = _interp(pel, tt)
                pts.append((P(x, y), pel[min(k, len(pel) - 1)].get("aire", False)))
                tt += 0.04
            x, y, k = _interp(pel, fin)
            pts.append((P(x, y), pel[min(k, len(pel) - 1)].get("aire", False)))
            if len(pts) > 1:
                piso = [p for p, aire in pts if not aire]
                glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                dg = ImageDraw.Draw(glow)
                for m in range(1, len(pts)):
                    (p0, _), (p1, aire) = pts[m - 1], pts[m]
                    if aire and (m // 3) % 2:
                        continue
                    dg.line([p0, p1], fill=ACENTO + (110,), width=int(22 * s))
                    d.line([p0, p1], fill=TEXTO + (255,), width=int(7 * s))
                capa.alpha_composite(glow)
                d = ImageDraw.Draw(capa)
        # jugadores (de lejos a cerca)
        orden = sorted(jugadores, key=lambda j: jug_pos(j, t)[1])
        for j in orden:
            x, y = jug_pos(j, t)
            sx, sy = P(x, y)
            venc = j.get("vencido")
            apag = venc is not None and t >= venc
            al = int(255 * a * (0.38 if apag else 1.0))
            col = color_arg if j.get("equipo", "rival") == "arg" else color_rival
            cara = caras.get(j["nombre"])
            if cara is not None:
                r = 38 * s
                c = cara.resize((int(2 * r), int(2 * r)), Image.BILINEAR)
                if al < 255:
                    c.putalpha(c.getchannel("A").point(lambda v: int(v * al / 255)))
                capa.alpha_composite(c, (int(sx - r), int(sy - r)))
                d.ellipse([sx - r, sy - r, sx + r, sy + r], outline=ACENTO + (al,), width=int(5 * s))
            else:
                r = 20 * s
                d.ellipse([sx - r, sy - r * 0.75, sx + r, sy + r * 0.75], fill=(0, 0, 0, int(al * 0.4)))
                d.ellipse([sx - r, sy - r - 6 * s, sx + r, sy + r - 6 * s], fill=col + (al,),
                          outline=OSCURO + (al,), width=int(3 * s))
            if venc is not None and 0 <= t - venc < 0.5:  # aro que se expande al dejarlo atrás
                u = (t - venc) / 0.5
                rr = r + 60 * s * u
                d.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], outline=ACENTO + (int(255 * (1 - u)),), width=int(5 * s))
            if j.get("nombre") and al > 0:
                nom = j["nombre"].upper()
                tw = d.textlength(nom, font=f_nom)
                yy = sy + r + 6 * s
                fondo_c = (ACENTO if cara is not None else CLARO)
                d.rectangle([sx - tw / 2 - 8 * s, yy, sx + tw / 2 + 8 * s, yy + 30 * s], fill=fondo_c + (al,))
                d.text((sx - tw / 2, yy + 3 * s), nom, font=f_nom, fill=OSCURO + (al,))
                if j.get("etiqueta") and not apag:
                    et = j["etiqueta"].upper()
                    tw2 = d.textlength(et, font=f_et)
                    d.rectangle([sx - tw2 / 2 - 6 * s, yy - 26 * s, sx + tw2 / 2 + 6 * s, yy - 2 * s], fill=OSCURO + (int(al * 0.85),))
                    d.text((sx - tw2 / 2, yy - 24 * s), et, font=f_et, fill=CLARO + (al,))
        # la pelota
        if t >= t_ini - 0.5:
            x, y, k = _interp(pel, t)
            sx, sy = P(x, y)
            seg = pel[min(k, len(pel) - 1)]
            alt = 0.0
            if seg.get("aire") and k > 0:
                u = (t - pel[k - 1]["t"]) / max(1e-6, seg["t"] - pel[k - 1]["t"])
                alt = math.sin(math.pi * max(0, min(1, u))) * float(seg.get("altura", 120)) * s
            rb = 11 * s * (1 + alt / (300 * s))
            d.ellipse([sx - rb * 1.3, sy - rb * 0.5, sx + rb * 1.3, sy + rb * 0.5], fill=(0, 0, 0, 110))
            d.ellipse([sx - rb, sy - alt - rb, sx + rb, sy - alt + rb], fill=TEXTO + (255,), outline=OSCURO + (255,), width=int(2 * s))
        # marca, título, etiqueta
        _marca(d, s, int(255 * a))
        if etiqueta:
            d.rectangle([xl, 136 * s, xl + 46 * s * a, 140 * s], fill=ACENTO + (int(255 * a),))
            _espaciado(d, (xl + 62 * s, 122 * s), etiqueta.upper(), f_e, ACENTO + (int(255 * a),), 4 * s)
        if titulo:
            d.text((xl, 162 * s), titulo.upper(), font=f_ti, fill=TEXTO + (int(255 * a),))
        if minuto:
            b = ease((t - 0.2) / 0.5)
            tw = d.textlength(minuto, font=f_min)
            d.text((W - 80 * s - tw + (1 - b) * 40 * s, 40 * s), minuto, font=f_min, fill=(0, 0, 0, 0),
                   stroke_width=int(3 * s), stroke_fill=ACENTO + (int(150 * b),))
        # contador de metros y segundos
        if contador and t >= contador["desde"]:
            tt = min(t, contador["hasta"])
            seg_c = tt - contador["desde"]
            m = largo_hasta(tt) - largo_hasta(contador["desde"])
            yb = 250 * s
            for k2, (val, uni) in enumerate(((f"{m:.0f}", "METROS"), (f"{seg_c:.1f}".replace(".", ","), "SEGUNDOS"))):
                xx = W - 96 * s - 300 * s * (1 - k2)
                tw = d.textlength(val, font=f_cont)
                d.text((xx - tw, yb), val, font=f_cont, fill=TEXTO + (255,))
                tw2 = d.textlength(uni, font=f_cl)
                d.text((xx - tw2, yb + 74 * s), uni, font=f_cl, fill=ACENTO + (255,))
        # datos grandes abajo
        for dt in datos:
            t0, t1 = dt["t"]
            if not (t0 <= t < t1):
                continue
            b = ease((t - t0) / 0.3)
            esc = 1.4 - 0.4 * b
            A_ = dt["a"]
            fa = fuente(700, 92 * s * esc)
            tw = d.textlength(A_, font=fa)
            d.text(((W - tw) / 2, H - 230 * s), A_, font=fa, fill=TEXTO + (int(255 * b),),
                   stroke_width=int(4 * s), stroke_fill=(0, 0, 0, int(140 * b)))
            if dt.get("b"):
                b2 = ease((t - t0 - 0.2) / 0.3)
                tw2 = d.textlength(dt["b"], font=f_db)
                yy = H - 120 * s + (1 - b2) * 16 * s
                d.rectangle([(W - tw2) / 2 - 20 * s, yy, (W + tw2) / 2 + 20 * s, yy + 50 * s], fill=CLARO + (int(255 * b2),))
                d.text(((W - tw2) / 2, yy + 8 * s), dt["b"], font=f_db, fill=FONDO + (int(255 * b2),))
        return capa

    _render(dest, W, H, dur, cuadro, fondo)


# ---------- insignia del canal sobre la marca de agua de una fuente (pedido del usuario, 11/11) ----------
def fantasma(src, dest, W, H, dur, texto, sub="", t0=0.5, flechas=(), foco=None):
    """Alternativa al golpe (pedido del usuario, 11/11: "que esté ahí pero no ocupe toda la pantalla"): en t0 el clip
    se CONGELA y la cámara se acerca despacio hacia `foco` (x, y en 0-1); el resultado aparece como número gigante
    solo de contorno, semitransparente, abajo a la derecha; `sub` en un chip abajo a la izquierda; y las `flechas`
    [{"a": (x, y) 0-1, "texto": "LA MANO DE DIOS", "t": seg, "desde": (x, y) opcional}] señalan un punto del cuadro
    congelado con una etiqueta verde (la línea crece desde la etiqueta hasta el punto)."""
    import math
    s = W / 1920
    f_g = fuente(800, 520 * s)
    f_sub = fuente(700, 40 * s)
    f_fl = fuente(800, 38 * s)
    n = round(dur * FPS)
    d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    bb = d0.textbbox((0, 0), texto, font=f_g, stroke_width=int(6 * s))
    wg, hg = bb[2] - bb[0], bb[3] - bb[1]
    num = Image.new("RGBA", (int(wg + 40 * s), int(hg + 40 * s)), (0, 0, 0, 0))
    ImageDraw.Draw(num).text((20 * s - bb[0], 20 * s - bb[1]), texto, font=f_g, fill=(0, 0, 0, 0),
                             stroke_width=int(6 * s), stroke_fill=TEXTO + (255,))
    foco_px = ((foco[0] if foco else 0.5) * W, (foco[1] if foco else 0.5) * H)
    resto = max(0.5, dur - t0)

    def pos(p, k, z):
        """Punto del cuadro original (0-1) -> píxel en pantalla con el zoom k (0-1) aplicado."""
        cx = W / 2 + (foco_px[0] - W / 2) * k
        cy = H / 2 + (foco_px[1] - H / 2) * k
        x0, y0 = cx - W / (2 * z), cy - H / (2 * z)
        return ((p[0] * W - x0) * z, (p[1] * H - y0) * z)

    p_in = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(src), "-frames:v", str(n), "-f", "rawvideo",
                             "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    p = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", "-an", str(dest)], stdin=subprocess.PIPE)
    tam = W * H * 3
    ultimo = Image.new("RGB", (W, H))
    congelado = None
    recientes = []

    def nitidez(im):
        g = im.convert("L").resize((480, 270), Image.BILINEAR)
        from PIL import ImageFilter, ImageStat
        return ImageStat.Stat(g.filter(ImageFilter.FIND_EDGES)).var[0]

    for i in range(n):
        buf = p_in.stdout.read(tam)
        if len(buf) == tam and congelado is None:
            ultimo = Image.frombytes("RGB", (W, H), buf)
            recientes = (recientes + [ultimo])[-3:]
        t = i / FPS - t0
        if t < 0:
            p.stdin.write(ultimo.tobytes())
            continue
        if congelado is None:
            cands = list(recientes)
            for _ in range(3):  # también los 3 cuadros que siguen
                buf = p_in.stdout.read(tam)
                if len(buf) == tam:
                    cands.append(Image.frombytes("RGB", (W, H), buf))
            congelado = max(cands, key=nitidez)
        k = min(1.0, t / resto)
        z = 1 + 0.12 * k
        cx = W / 2 + (foco_px[0] - W / 2) * k
        cy = H / 2 + (foco_px[1] - H / 2) * k
        x0, y0 = cx - W / (2 * z), cy - H / (2 * z)
        img = congelado.crop((int(x0), int(y0), int(x0 + W / z), int(y0 + H / z))).resize((W, H), Image.BILINEAR).convert("RGBA")
        img = Image.alpha_composite(img, Image.new("RGBA", (W, H), OSCURO + (int(60 * ease(t / 0.3)),)))
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        # número fantasma: aparece con un pop
        a = ease(t / 0.3)
        esc = 1 + 0.25 * (1 - ease(t / 0.3))
        c = num if esc == 1 else num.resize((int(num.width * esc), int(num.height * esc)), Image.BILINEAR)
        c = c.copy()
        c.putalpha(c.getchannel("A").point(lambda v: int(v * 0.72 * a)))
        capa.alpha_composite(c, (int(W - 50 * s - c.width), int(H - 30 * s - c.height)))
        # chip con el detalle
        if sub:
            b = ease((t - 0.2) / 0.3)
            if b > 0:
                w = d.textlength(sub, font=f_sub) + 44 * s
                x = 60 * s - (1 - b) * 40 * s
                y = H - 150 * s
                d.rectangle([x, y, x + w, y + 66 * s], fill=OSCURO + (int(235 * b),))
                d.text((x + 22 * s, y + 10 * s), sub, font=f_sub, fill=TEXTO + (int(255 * b),))
        # flechas
        for f in flechas:
            tf = f.get("t", 0.4) - t0  # "t" cuenta desde el inicio de la pieza
            if t < tf:
                continue
            b = ease((t - tf) / 0.35)
            P = pos(f["a"], k, z)
            if f.get("desde"):
                L = pos(f["desde"], k, z)
            else:
                dx = -260 * s if P[0] > W * 0.55 else 260 * s
                dy = 200 * s if P[1] < H * 0.4 else -200 * s
                L = (P[0] + dx, P[1] + dy)
            E = (L[0] + (P[0] - L[0]) * b, L[1] + (P[1] - L[1]) * b)
            d.line([L, E], fill=ACENTO + (255,), width=int(5 * s))
            if b >= 1:
                r = 11 * s + 4 * s * math.sin((t - tf) * 6)
                d.ellipse([P[0] - r, P[1] - r, P[0] + r, P[1] + r], outline=ACENTO + (255,), width=int(4 * s))
            tw = d.textlength(f["texto"], font=f_fl)
            lb = ease((t - tf - 0.1) / 0.25)
            if lb > 0:
                ww, hh = (tw + 36 * s) * (0.9 + 0.1 * lb), 58 * s * (0.9 + 0.1 * lb)
                lx = L[0] - ww / 2
                ly = L[1] - hh / 2
                d.rounded_rectangle([lx, ly, lx + ww, ly + hh], radius=int(6 * s), fill=ACENTO + (int(255 * lb),))
                d.text((L[0] - tw / 2, L[1] - 22 * s), f["texto"], font=f_fl, fill=OSCURO + (int(255 * lb),))
        img = Image.alpha_composite(img, capa)
        flash = int(110 * max(0.0, 1 - t / 0.15))
        if flash:
            img = Image.alpha_composite(img, Image.new("RGBA", (W, H), (255, 255, 255, flash)))
        p.stdin.write(img.convert("RGB").tobytes())
    p_in.stdout.close()
    p_in.wait()
    p.stdin.close()
    if p.wait() != 0:
        raise SystemExit(f"ffmpeg falló renderizando {dest}")


def insignia(dest, W, H, caja):
    """PNG WxH transparente con una insignia "LOS 11" que tapa la marca de agua del canal de origen.
    caja = (x, y, w, h) en píxeles del cuadro final."""
    x, y, w, h = caja
    s = W / 1920
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x, y, x + w, y + h], radius=int(10 * s), fill=OSCURO + (225,))
    d.rectangle([x + 18 * s, y + 22 * s, x + 26 * s, y + h - 22 * s], fill=ACENTO + (255,))
    f = fuente(800, int(h * 0.46))
    f2 = fuente(500, int(h * 0.17))
    d.text((x + 44 * s, y + h * 0.14), CANAL, font=f, fill=TEXTO + (255,))
    _espaciado(d, (x + 46 * s, y + h * 0.66), "ARCHIVO", f2, ACENTO + (255,), 4 * s)
    img.save(dest)


# ---------- charla: tarjetas de cita con foto real de quien habla (pedido del usuario, 11/11) ----------
def _cubrir(ruta, w, h, recorte=None):
    """Foto recortada "cover" a w x h (cacheada), apenas desaturada. recorte = (x0, y0, x1, y1) en la foto original."""
    clave = (str(ruta), int(w), int(h), tuple(recorte) if recorte else None)
    if clave not in _cubrir.cache:
        from PIL import ImageEnhance
        im = Image.open(ruta).convert("RGB")
        if recorte:
            im = im.crop(tuple(int(v) for v in recorte))
        iw, ih = im.size
        if iw / ih > w / h:
            nw = ih * w / h
            im = im.crop((int((iw - nw) / 2), 0, int((iw + nw) / 2), ih))
        else:
            nh = iw * h / w
            im = im.crop((0, int((ih - nh) / 2), iw, int((ih + nh) / 2)))
        im = ImageEnhance.Color(im.resize((int(w), int(h)), Image.LANCZOS)).enhance(0.85)
        _cubrir.cache[clave] = im
    return _cubrir.cache[clave]


_cubrir.cache = {}


def _persona(d, cx, base_y, alto, color, alpha=255, ancho=0.3):
    """Silueta sencilla (cabeza + hombros) de `alto` px apoyada en base_y."""
    r = alto * 0.17
    d.ellipse([cx - r, base_y - alto, cx + r, base_y - alto + 2 * r], fill=color + (alpha,))
    d.rounded_rectangle([cx - alto * ancho, base_y - alto + 2.25 * r, cx + alto * ancho, base_y],
                        radius=int(alto * 0.14), fill=color + (alpha,))


def charla(dest, W, H, dur, globos, titulo="", etiqueta="", fondo=None):
    """Citas reales, una por vez, como tarjetas: la foto de quien habla a un costado (o, si no hay foto, el nombre del
    medio como cabecera de diario) y la frase grande al otro. globos = [{"lado": "izq"|"der", "quien": "Menotti",
    "fuente": "campeón del mundo 1978", "texto": "...", "t": seg, "foto": ruta opcional}]. Cada cita entra con la foto
    barriendo desde su lado y las líneas de texto subiendo; la anterior se va hacia su lado."""
    s = W / 1920
    f_tx = fuente(600, 62 * s, plex=True)
    f_q = fuente(800, 190 * s, plex=True)
    f_nom = fuente(800, 30 * s)
    f_src = fuente(500, 22 * s)
    f_medio = fuente(700, 60 * s, plex=True)
    f_e = fuente(500, 26 * s)
    f_ti = fuente(700, 44 * s)
    xl = 96 * s
    pw, ph = 540 * s, 690 * s
    py = (H - ph) / 2 + 40 * s
    fotos = {}
    for g in globos:
        if g.get("foto"):
            fotos[g["foto"]] = _cubrir(g["foto"], pw, ph, g.get("recorte"))
    ancho_tx = W - 2 * 120 * s - pw - 90 * s

    def tarjeta(capa, g, a, salida=0.0):
        """a = entrada 0-1; salida = 0-1 (se va)."""
        d = ImageDraw.Draw(capa)
        lado = g.get("lado", "izq")
        izq = lado == "izq"
        al = int(255 * a * (1 - salida))
        dx = -salida * 60 * s if izq else salida * 60 * s
        px = (120 * s if izq else W - 120 * s - pw) + dx
        # foto (barrido desde su lado) o cabecera de medio
        foto = fotos.get(g.get("foto"))
        panel = Image.new("RGBA", (int(pw), int(ph)), (0, 0, 0, 0))
        if foto is not None:
            panel.paste(foto, (0, 0))
        else:
            pd = ImageDraw.Draw(panel)
            pd.rectangle([0, 0, pw, ph], fill=PANEL + (255,))
            nom = g["quien"].upper()
            fm = f_medio
            while pd.textlength(nom, font=fm) > pw - 60 * s and fm.size > 30 * s:
                fm = fuente(700, fm.size - 4, plex=True)
            tw = pd.textlength(nom, font=fm)
            pd.line([40 * s, ph * 0.40, pw - 40 * s, ph * 0.40], fill=TEXTO + (255,), width=int(3 * s))
            pd.text(((pw - tw) / 2, ph * 0.40 + 20 * s), nom, font=fm, fill=TEXTO + (255,))
            pd.line([40 * s, ph * 0.40 + 50 * s + fm.size, pw - 40 * s, ph * 0.40 + 50 * s + fm.size], fill=TEXTO + (255,), width=int(3 * s))
            if g.get("fuente"):
                fs = fuente(500, 22 * s)
                tw = pd.textlength(g["fuente"].upper(), font=fs)
                pd.text(((pw - tw) / 2, ph * 0.40 + 70 * s + fm.size), g["fuente"].upper(), font=fs, fill=ACENTO + (255,))
        vis = int(pw * ease(a / 0.6))
        if vis > 0:
            parte = panel.crop((0, 0, vis, int(ph))) if izq else panel.crop((int(pw) - vis, 0, int(pw), int(ph)))
            if al < 255:
                parte.putalpha(parte.getchannel("A").point(lambda v: v * al // 255))
            capa.alpha_composite(parte, (int(px) if izq else int(px + pw - vis), int(py)))
            d = ImageDraw.Draw(capa)
            d.rectangle([px, py, px + pw, py + ph], outline=TEXTO + (int(al * 0.5),), width=int(2 * s))
        # nombre y fuente debajo de la foto
        if a > 0.5 and foto is not None:
            b = int(al * ease((a - 0.5) / 0.3))
            nom = g["quien"].upper()
            tw = d.textlength(nom, font=f_nom)
            cx = px + pw / 2
            d.rectangle([cx - tw / 2 - 16 * s, py + ph + 18 * s, cx + tw / 2 + 16 * s, py + ph + 62 * s], fill=ACENTO + (b,))
            d.text((cx - tw / 2, py + ph + 24 * s), nom, font=f_nom, fill=OSCURO + (b,))
            if g.get("fuente"):
                tw = d.textlength(g["fuente"].upper(), font=f_src)
                d.text((cx - tw / 2, py + ph + 76 * s), g["fuente"].upper(), font=f_src, fill=CLARO + (b,))
        # la frase
        tx0 = (px + pw + 90 * s) if izq else (120 * s + dx)
        lineas = _partir(g["texto"], f_tx, ancho_tx)
        lh = 80 * s
        alto_tx = lh * len(lineas)
        ty0 = H / 2 - alto_tx / 2 + 30 * s
        q_a = int(al * ease((a - 0.15) / 0.3))
        d.text((tx0 - 10 * s, ty0 - 165 * s), "“", font=f_q, fill=ACENTO + (q_a,))
        for j, ln in enumerate(lineas):
            b = ease((a - 0.25 - j * 0.08) / 0.3)
            if b <= 0:
                continue
            d.text((tx0, ty0 + j * lh + (1 - b) * 18 * s), ln, font=f_tx, fill=TEXTO + (int(al * b),))
        b = ease((a - 0.35 - len(lineas) * 0.08) / 0.3)
        if b > 0 and foto is None:
            d.rectangle([tx0, ty0 + alto_tx + 26 * s, tx0 + 60 * s * b, ty0 + alto_tx + 30 * s], fill=ACENTO + (int(al * b),))
            src = " · ".join(x for x in (g.get("quien"), g.get("fuente")) if x)
            _espaciado(d, (tx0 + 80 * s, ty0 + alto_tx + 16 * s), src.upper(), f_src, CLARO + (int(al * b),), 3 * s)
        elif b > 0:
            d.rectangle([tx0, ty0 + alto_tx + 26 * s, tx0 + 60 * s * b, ty0 + alto_tx + 30 * s], fill=ACENTO + (int(al * b),))

    def cuadro(t, i, n):
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        a = ease(t / 0.4)
        _marca(d, s, int(255 * a))
        if etiqueta:
            d.rectangle([xl, 136 * s, xl + 46 * s * a, 140 * s], fill=ACENTO + (int(255 * a),))
            _espaciado(d, (xl + 62 * s, 122 * s), etiqueta.upper(), f_e, ACENTO + (int(255 * a),), 4 * s)
        if titulo:
            d.text((xl, 162 * s), titulo.upper(), font=f_ti, fill=TEXTO + (int(255 * a),))
        activos = [g for g in globos if t >= g["t"]]
        if not activos:
            return capa
        actual = activos[-1]
        if len(activos) >= 2:
            prev = activos[-2]
            sal = ease((t - actual["t"]) / 0.3)
            if sal < 1:
                tarjeta(capa, prev, 1.0, sal)
        tarjeta(capa, actual, min(1.0, (t - actual["t"]) / 1.0))
        return capa

    _render(dest, W, H, dur, cuadro, fondo)


# ---------- altura: medir a un jugador contra otro, con fotos reales (pedido del usuario, 11/11) ----------
def altura(dest, W, H, dur, personas, titulo="", etiqueta="", fondo=None):
    """Columnas con la foto de cada persona, de alto proporcional a su altura real, que suben desde el piso mientras el
    número cuenta. personas = [{"nombre": "Maradona", "altura": 1.65, "foto": ruta, "recorte": (x0,y0,x1,y1) opcional,
    "t": seg, "sub": "el capitán"}] (hasta 3, de izquierda a derecha). Al final, la diferencia en centímetros."""
    s = W / 1920
    f_num = fuente(800, 150 * s)
    f_m = fuente(700, 44 * s)
    f_lab = fuente(700, 36 * s)
    f_nom = fuente(800, 30 * s)
    f_sub = fuente(500, 26 * s, plex=True)
    f_tick = fuente(500, 20 * s)
    f_e = fuente(500, 26 * s)
    f_ti = fuente(700, 44 * s)
    f_dif = fuente(800, 64 * s)
    xl = 96 * s
    base_y = H - 150 * s
    px_m = 360 * s  # píxeles por metro
    cw = 300 * s
    paso = 420 * s
    maxh = max(p["altura"] for p in personas)
    n = len(personas)
    xs = [W * 0.60 + (k - (n - 1) / 2) * paso for k in range(n)]
    x_regla = xs[0] - cw / 2 - 70 * s
    cols = {}
    for p in personas:
        if p.get("foto"):
            cols[p["nombre"]] = _cubrir(p["foto"], cw, p["altura"] * px_m, p.get("recorte"))

    def cuadro(t, i, nn):
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        a = ease(t / 0.4)
        _marca(d, s, int(255 * a))
        if etiqueta:
            d.rectangle([xl, 196 * s, xl + 46 * s * a, 200 * s], fill=ACENTO + (int(255 * a),))
            _espaciado(d, (xl + 62 * s, 182 * s), etiqueta.upper(), f_e, ACENTO + (int(255 * a),), 4 * s)
        if titulo:
            d.text((xl, 222 * s), titulo.upper(), font=f_ti, fill=TEXTO + (int(255 * a),))
        # piso y regla
        d.line([x_regla - 40 * s, base_y, xs[-1] + cw / 2 + 160 * s, base_y], fill=CLARO + (int(200 * a),), width=int(3 * s))
        top = base_y - (maxh + 0.12) * px_m
        d.line([x_regla, base_y, x_regla, base_y - (base_y - top) * a], fill=CLARO + (160,), width=int(3 * s))
        cm = 0
        while cm <= (maxh + 0.12) * 100:
            y = base_y - cm / 100 * px_m
            if y < base_y - (base_y - top) * a:
                break
            largo = 22 if cm % 50 == 0 else (12 if cm % 10 == 0 else 0)
            if largo:
                d.line([x_regla - largo * s, y, x_regla, y], fill=CLARO + (160,), width=int(2 * s))
            if cm % 50 == 0:
                txt = f"{cm / 100:.2f}".replace(".", ",")
                tw = d.textlength(txt, font=f_tick)
                d.text((x_regla - 34 * s - tw, y - 12 * s), txt, font=f_tick, fill=CLARO + (200,))
            cm += 10
        ultimo = None
        for k, p in enumerate(personas):
            if t < p["t"]:
                continue
            b = ease((t - p["t"]) / 1.2)
            h_act = p["altura"] * b
            x = xs[k]
            hp = h_act * px_m
            col = ACENTO if k == 0 else CLARO
            col_img = cols.get(p["nombre"])
            if hp > 2:
                if col_img is not None:
                    hf = col_img.height
                    parte = col_img.crop((0, int(hf - hp), int(cw), hf))
                    capa.paste(parte, (int(x - cw / 2), int(base_y - hp)))
                    d = ImageDraw.Draw(capa)
                else:
                    _persona(d, x, base_y, hp, col, 230, ancho=0.16)
                d.rectangle([x - cw / 2, base_y - hp, x + cw / 2, base_y], outline=col + (255,), width=int(3 * s))
            # línea de altura hasta la regla y número grande contando
            y = base_y - hp
            d.line([x_regla, y, x - cw / 2, y], fill=col + (200,), width=int(2 * s))
            txt = f"{h_act:.2f}".replace(".", ",")
            if 0 < b < 1 or (k == n - 1 and t < p["t"] + 1.6):
                d.text((xl, 300 * s), txt, font=f_num, fill=TEXTO + (255,))
                d.text((xl + d.textlength(txt, font=f_num) + 24 * s, 380 * s), "m", font=f_m, fill=ACENTO + (255,))
            if b >= 1:
                lab = txt + " m"
                tw = d.textlength(lab, font=f_lab)
                d.rectangle([x - tw / 2 - 12 * s, y - 62 * s, x + tw / 2 + 12 * s, y - 14 * s], fill=col + (255,))
                d.text((x - tw / 2, y - 58 * s), lab, font=f_lab, fill=OSCURO + (255,))
            nom = p["nombre"].upper()
            tw = d.textlength(nom, font=f_nom)
            d.rectangle([x - tw / 2 - 14 * s, base_y + 16 * s, x + tw / 2 + 14 * s, base_y + 58 * s], fill=col + (255,))
            d.text((x - tw / 2, base_y + 21 * s), nom, font=f_nom, fill=OSCURO + (255,))
            if p.get("sub"):
                tw = d.textlength(p["sub"], font=f_sub)
                d.text((x - tw / 2, base_y + 70 * s), p["sub"], font=f_sub, fill=CLARO + (255,))
            ultimo = (k, b)
        # diferencia
        if n >= 2 and ultimo and ultimo[0] == n - 1 and ultimo[1] >= 1:
            b2 = ease((t - personas[-1]["t"] - 1.2) / 0.4)
            dif = round((personas[-1]["altura"] - personas[0]["altura"]) * 100)
            y0, y1 = base_y - personas[0]["altura"] * px_m, base_y - personas[-1]["altura"] * px_m
            xm = xs[-1] + cw / 2 + 40 * s
            al = int(255 * b2)
            d.line([xs[0] + cw / 2, y0, xm, y0], fill=ACENTO + (al,), width=int(3 * s))
            d.line([xm, y0, xm, y1], fill=ACENTO + (al,), width=int(6 * s))
            d.line([xm - 14 * s, y1, xm + 14 * s, y1], fill=ACENTO + (al,), width=int(6 * s))
            d.line([xm - 14 * s, y0, xm + 14 * s, y0], fill=ACENTO + (al,), width=int(6 * s))
            txt = f"{dif:+d} cm"
            d.text((xm + 24 * s, (y0 + y1) / 2 - 36 * s), txt, font=f_dif, fill=ACENTO + (al,))
            d.text((xl, 300 * s), txt, font=f_num, fill=ACENTO + (al,))
        return capa

    _render(dest, W, H, dur, cuadro, fondo)


# ---------- cifras: números grandes que cuentan (pedido del usuario, 11/11: Malvinas con contexto) ----------
def cifras(dest, W, H, dur, items, titulo="", etiqueta="", fondo=None):
    """Hasta tres cifras en fila, cada una cuenta desde 0 cuando el narrador la nombra.
    items = [{"numero": 649, "texto": "SOLDADOS ARGENTINOS MUERTOS", "t": seg, "sufijo": ""}]."""
    s = W / 1920
    f_num = fuente(800, 170 * s)
    f_tx = fuente(600, 26 * s)
    f_e = fuente(500, 26 * s)
    f_ti = fuente(700, 44 * s)
    xl = 96 * s
    n = len(items)
    ancho = (W - 2 * xl) / n

    def cuadro(t, i, nn):
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        a = ease(t / 0.4)
        _marca(d, s, int(255 * a))
        if etiqueta:
            d.rectangle([xl, 136 * s, xl + 46 * s * a, 140 * s], fill=ACENTO + (int(255 * a),))
            _espaciado(d, (xl + 62 * s, 122 * s), etiqueta.upper(), f_e, ACENTO + (int(255 * a),), 4 * s)
        if titulo:
            d.text((xl, 162 * s), titulo.upper(), font=f_ti, fill=TEXTO + (int(255 * a),))
        for k, it in enumerate(items):
            if t < it["t"]:
                continue
            b = ease((t - it["t"]) / 1.3)
            cx = xl + ancho * (k + 0.5)
            val = int(round(it["numero"] * b))
            txt = f"{val:,}".replace(",", ".") + it.get("sufijo", "")
            tw = d.textlength(txt, font=f_num)
            d.text((cx - tw / 2, H * 0.36), txt, font=f_num, fill=(ACENTO if b >= 1 else TEXTO) + (255,))
            d.rectangle([cx - 30 * s, H * 0.36 + 200 * s, cx + 30 * s, H * 0.36 + 206 * s], fill=ACENTO + (255,))
            lineas = _partir(it["texto"].upper(), f_tx, ancho - 60 * s)
            for j, ln in enumerate(lineas):
                lw = _ancho_esp(ln, f_tx, 3 * s)
                _espaciado(d, (cx - lw / 2, H * 0.36 + 226 * s + j * 36 * s), ln, f_tx, CLARO + (255,), 3 * s)
        return capa

    _render(dest, W, H, dur, cuadro, fondo)


# ---------- cortos animados: pequeñas historias dibujadas (pedido del usuario, 11/11: "esas cosas definen el canal") ----------
def _camiseta(d, cx, cy, h, color, numero=None, alpha=255, borde=None, num_color=None, f=None):
    """Camiseta de frente (o de espaldas con número) de alto h centrada en (cx, cy)."""
    w = h * 0.86
    col = color + (alpha,)
    cuerpo = [(cx - w * 0.5, cy - h * 0.5), (cx - w * 0.22, cy - h * 0.5), (cx, cy - h * 0.42), (cx + w * 0.22, cy - h * 0.5),
              (cx + w * 0.5, cy - h * 0.5), (cx + w * 0.62, cy - h * 0.22), (cx + w * 0.42, cy - h * 0.1),
              (cx + w * 0.38, cy + h * 0.5), (cx - w * 0.38, cy + h * 0.5), (cx - w * 0.42, cy - h * 0.1),
              (cx - w * 0.62, cy - h * 0.22)]
    d.polygon(cuerpo, fill=col, outline=(borde + (alpha,)) if borde else None, width=max(1, int(h * 0.02)))
    if numero is not None:
        fn = f or fuente(800, h * 0.42)
        tw = d.textlength(str(numero), font=fn)
        d.text((cx - tw / 2, cy - h * 0.22), str(numero), font=fn, fill=(num_color or TEXTO) + (alpha,))


def _edificios(d, x0, x1, base_y, s, color, alpha=255, semilla=3):
    import random
    rnd = random.Random(semilla)
    x = x0
    while x < x1:
        w = rnd.randint(int(60 * s), int(140 * s))
        h = rnd.randint(int(80 * s), int(260 * s))
        d.rectangle([x, base_y - h, min(x + w, x1), base_y], fill=color + (alpha,))
        for wy in range(int(base_y - h + 18 * s), int(base_y - 10 * s), int(28 * s)):
            for wx in range(int(x + 12 * s), int(min(x + w, x1) - 14 * s), int(26 * s)):
                if rnd.random() < 0.55:
                    d.rectangle([wx, wy, wx + 10 * s, wy + 14 * s], fill=OSCURO + (alpha,))
        x += w + rnd.randint(int(10 * s), int(30 * s))


def _negocio(d, cx, base_y, s, alpha=255, activo=False, texto="CAMISETAS"):
    col = (ACENTO if activo else CLARO) + (alpha,)
    w, h = 220 * s, 170 * s
    d.rectangle([cx - w / 2, base_y - h, cx + w / 2, base_y], fill=PANEL + (alpha,), outline=col, width=int(4 * s))
    d.rectangle([cx - w / 2 - 14 * s, base_y - h - 34 * s, cx + w / 2 + 14 * s, base_y - h], fill=col)
    f = fuente(800, 22 * s)
    tw = d.textlength(texto, font=f)
    d.text((cx - tw / 2, base_y - h - 30 * s), texto, font=f, fill=OSCURO + (alpha,))
    d.rectangle([cx - 30 * s, base_y - 100 * s, cx + 30 * s, base_y], fill=OSCURO + (alpha,))
    d.rectangle([cx - w / 2 + 20 * s, base_y - 130 * s, cx - 50 * s, base_y - 40 * s], fill=OSCURO + (alpha,))
    d.rectangle([cx + 50 * s, base_y - 130 * s, cx + w / 2 - 20 * s, base_y - 40 * s], fill=OSCURO + (alpha,))


def corto_camisetas(dest, W, H, dur, parte, tiempos, fondo=None):
    """Corto animado de las camisetas de México 86 (pedido del usuario: "un pequeño cortometraje").
    parte 1: Inglaterra de blanco vs la azul gruesa -> 3 días -> Moschella recorre los negocios del DF -> uno.
    parte 2: dos modelos -> Diego elige -> 38 camisetas -> escudo cosido -> números plateados planchados.
    tiempos = {"blanco": s, "tres": s, "moschella": s, "negocio": s} o {"modelos", "elige", "treinta", "escudo", "numeros"}."""
    s = W / 1920
    f_e = fuente(500, 26 * s)
    f_lab = fuente(800, 30 * s)
    f_big = fuente(800, 150 * s)
    f_q = fuente(600, 40 * s, plex=True)
    xl = 96 * s
    AZUL = (28, 60, 130)
    AZUL_CLARO = (70, 130, 210)
    BLANCO = (235, 235, 235)
    PLATA = (205, 210, 220)
    cara = None
    if parte == 2:
        ruta = RAIZ / "proyectos" / "argentina-1986" / "material" / "retratos" / "caras" / "maradona.png"
        if ruta.exists():
            cara = _circulo(_retrato(ruta, int(180 * s)), ACENTO + (255,), 6 * s)
    T = {k: float(v) for k, v in tiempos.items()}

    def etiqueta(d, a, txt):
        d.rectangle([xl, 136 * s, xl + 46 * s * a, 140 * s], fill=ACENTO + (int(255 * a),))
        _espaciado(d, (xl + 62 * s, 122 * s), txt.upper(), f_e, ACENTO + (int(255 * a),), 4 * s)

    def chip(d, cx, y, txt, a, col=ACENTO, f=None):
        f = f or f_lab
        tw = d.textlength(txt, font=f)
        d.rectangle([cx - tw / 2 - 16 * s, y, cx + tw / 2 + 16 * s, y + f.size + 18 * s], fill=col + (int(255 * a),))
        d.text((cx - tw / 2, y + 8 * s), txt, font=f, fill=OSCURO + (int(255 * a),))

    def cuadro1(t, i, n):
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        a = ease(t / 0.4)
        _marca(d, s, int(255 * a))
        etiqueta(d, a, "Tres días antes de Inglaterra")
        base_y = H * 0.80
        mos = T.get("moschella", 1e9)
        if t < mos:
            # dos camisetas: Inglaterra (blanca) y la azul gruesa de Argentina
            b = ease((t - T.get("blanco", 0)) / 0.5)
            if b > 0:
                cxs = (W * 0.36, W * 0.64)
                _camiseta(d, cxs[0], H * 0.48, 300 * s, BLANCO, alpha=int(255 * b), borde=CLARO)
                chip(d, cxs[0], H * 0.70, "INGLATERRA · BLANCA", b, col=CLARO)
                c = ease((t - T.get("blanco", 0) - 0.4) / 0.5)
                if c > 0:
                    _camiseta(d, cxs[1], H * 0.48, 300 * s, AZUL, alpha=int(255 * c), borde=CLARO)
                    chip(d, cxs[1], H * 0.70, "ARGENTINA · AZUL, DE ALGODÓN GRUESO", c, col=CLARO)
                    # "pesada": gotas de sudor
                    for k in range(4):
                        gy = H * 0.48 + ((t * 120 + k * 60) % 180) * s - 60 * s
                        d.ellipse([cxs[1] + (k - 1.5) * 50 * s - 6 * s, gy, cxs[1] + (k - 1.5) * 50 * s + 6 * s, gy + 16 * s],
                                  fill=AZUL_CLARO + (int(200 * c),))
            tr = ease((t - T.get("tres", 1e9)) / 0.4)
            if tr > 0:
                txt = "3 DÍAS"
                tw = d.textlength(txt, font=f_big)
                d.rounded_rectangle([W / 2 - tw / 2 - 40 * s, H * 0.30, W / 2 + tw / 2 + 40 * s, H * 0.30 + 200 * s], radius=int(16 * s), fill=OSCURO + (int(230 * tr),))
                d.text((W / 2 - tw / 2, H * 0.30 + 10 * s), txt, font=f_big, fill=TEXTO + (int(255 * tr),))
                chip(d, W / 2, H * 0.30 + 210 * s, "PARA EL PARTIDO CONTRA INGLATERRA", tr)
        else:
            # Moschella recorre el DF: ciudad que se desplaza, negocios que pasan
            m = t - mos
            _edificios(d, 0, W, base_y - 60 * s, s, PANEL, 255)
            d.rectangle([0, base_y - 60 * s, W, base_y + 20 * s], fill=OSCURO + (255,))
            neg = T.get("negocio", 1e9)
            parado = t >= neg
            vel = (W * 0.9 + 2 * 640 * s - W * 0.66) / max(0.5, neg - mos)  # el 3er negocio frena en x = 0.66 W
            desp = vel * min(m, max(0.0, neg - mos))
            xs = [W * 0.9 + k * 640 * s - desp for k in range(6)]
            for k, x in enumerate(xs):
                if -200 * s < x < W + 200 * s:
                    ultimo = k == 2
                    _negocio(d, x, base_y - 60 * s, s, 255, activo=parado and ultimo,
                             texto=["ZAPATOS", "ROPA", "CAMISETAS", "DEPORTES", "MERCADO", "ROPA"][k])
                    if not parado or not ultimo:
                        f = fuente(800, 60 * s)
                        d.text((x - 16 * s, base_y - 330 * s), "?", font=f, fill=CLARO + (255,))
            # Moschella: silueta caminando (piernas alternan)
            px = W * 0.42
            paso = math.sin(m * 10) * 16 * s if not parado else 0
            _persona(d, px, base_y - 70 * s, 220 * s, ACENTO, 255, ancho=0.22)
            d.line([px - 10 * s, base_y - 70 * s, px - 24 * s + paso, base_y + 10 * s], fill=ACENTO + (255,), width=int(16 * s))
            d.line([px + 10 * s, base_y - 70 * s, px + 24 * s - paso, base_y + 10 * s], fill=ACENTO + (255,), width=int(16 * s))
            d.rounded_rectangle([px - 70 * s, base_y - 170 * s, px - 30 * s, base_y - 110 * s], radius=int(6 * s), fill=OSCURO + (255,))  # portafolio
            chip(d, px, base_y - 330 * s, "RUBÉN MOSCHELLA · AYUDANTE DE BILARDO", ease(m / 0.4))
            if parado:
                q = ease((t - neg) / 0.4)
                chip(d, W / 2, H * 0.18, "ACÁ. CAMISETAS DE TODOS LOS COLORES.", q, col=TEXTO, f=f_q)
            else:
                chip(d, W / 2, H * 0.18, "RECORRIENDO LOS NEGOCIOS DE CIUDAD DE MÉXICO", ease(m / 0.4), col=TEXTO, f=f_q)
        return capa

    def cuadro2(t, i, n):
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        a = ease(t / 0.4)
        _marca(d, s, int(255 * a))
        etiqueta(d, a, "La camiseta azul")
        t_mod, t_el, t_38, t_esc, t_num = (T.get(k, 1e9) for k in ("modelos", "elige", "treinta", "escudo", "numeros"))
        cy = H * 0.50
        if t < t_38:
            b = ease((t - t_mod) / 0.5)
            if b > 0:
                el = ease((t - t_el) / 0.5)
                for k, (cx, col, nom) in enumerate(((W * 0.33, AZUL_CLARO, "MODELO 1 · AZUL CLARO"), (W * 0.60, AZUL, "MODELO 2 · AZUL OSCURO"))):
                    al = int(255 * b * (1 if (el <= 0 or k == 1) else 0.35))
                    esc = 1 + 0.12 * el if k == 1 else 1
                    _camiseta(d, cx, cy, 320 * s * esc, col, alpha=al, borde=CLARO)
                    chip(d, cx, cy + 190 * s, nom, b * (1 if (el <= 0 or k == 1) else 0.4), col=CLARO)
                if el > 0:
                    if cara is not None:
                        c = cara.copy()
                        c.putalpha(c.getchannel("A").point(lambda v: int(v * el)))
                        capa.alpha_composite(c, (int(W * 0.80 - 90 * s), int(cy - 90 * s - (1 - el) * 30 * s)))
                        d = ImageDraw.Draw(capa)
                    d.line([W * 0.80 - 100 * s, cy + 40 * s, W * 0.60 + 150 * s, cy], fill=ACENTO + (int(255 * el),), width=int(5 * s))
                    chip(d, W * 0.5, H * 0.16, "“CON ESTA LE GANAMOS A INGLATERRA”", el, col=TEXTO, f=f_q)
                    chip(d, W * 0.80, cy + 120 * s, "MARADONA", el)
        else:
            m = t - t_38
            # 38 camisetas en grilla, con contador
            cols, filas = 10, 4
            total = 38
            vistas = min(total, int(m / 1.4 * total) + 1) if t < t_esc else total
            cw, ch = 150 * s, 120 * s
            x0 = W / 2 - cols * cw / 2 + cw / 2
            y0 = H * 0.32
            esc_a = ease((t - t_esc) / 0.5)
            num_a = ease((t - t_num) / 0.5)
            for k in range(vistas):
                cx = x0 + (k % cols) * cw
                cyy = y0 + (k // cols) * ch
                if t >= t_esc and k == 0:
                    continue
                _camiseta(d, cx, cyy, 100 * s, AZUL, alpha=int(255 * (0.35 if (esc_a > 0) else 1)), borde=CLARO,
                          numero=(k + 1 if num_a > 0 else None), num_color=PLATA, f=fuente(800, 40 * s))
            if t < t_esc:
                txt = str(vistas)
                tw = d.textlength(txt, font=f_big)
                d.text((W / 2 - tw / 2, H * 0.66), txt, font=f_big, fill=(ACENTO if vistas == total else TEXTO) + (255,))
                chip(d, W / 2, H * 0.66 + 170 * s, "CAMISETAS COMPRADAS", ease(m / 0.3))
            else:
                # una camiseta grande: le cosen el escudo, le planchan el número
                cx, cyy = W * 0.5, H * 0.56
                _camiseta(d, cx, cyy, 420 * s, AZUL, alpha=255, borde=CLARO)
                # escudo (vuela desde la derecha)
                ex = cx - 70 * s + (1 - esc_a) * 500 * s
                ey = cyy - 90 * s
                r = 36 * s
                ea = esc_a * (1 - num_a)
                d.polygon([(ex - r, ey - r), (ex + r, ey - r), (ex + r, ey + r * 0.4), (ex, ey + r * 1.2), (ex - r, ey + r * 0.4)],
                          fill=AZUL_CLARO + (int(255 * ea),), outline=TEXTO + (int(255 * ea),), width=int(3 * s))
                fs = fuente(800, 22 * s)
                d.text((ex - d.textlength("AFA", font=fs) / 2, ey - 16 * s), "AFA", font=fs, fill=TEXTO + (int(255 * ea),))
                if esc_a >= 1 and num_a <= 0:
                    # puntadas alrededor
                    for k in range(8):
                        ang = k / 8 * 6.283 + t * 2
                        d.line([ex + math.cos(ang) * (r + 8 * s), ey + math.sin(ang) * (r + 8 * s),
                                ex + math.cos(ang) * (r + 18 * s), ey + math.sin(ang) * (r + 18 * s)], fill=TEXTO + (255,), width=int(3 * s))
                chip(d, W * 0.5, H * 0.16, "LE COSIERON EL ESCUDO", esc_a if num_a <= 0 else 0.0)
                if num_a > 0:
                    # número plateado, planchado (la plancha pasa y lo revela)
                    fn = fuente(800, 230 * s)
                    tw = d.textlength("10", font=fn)
                    nx, ny = cx - tw / 2, cyy - 120 * s
                    rev = int(tw * ease((t - t_num - 0.2) / 0.9))
                    cap = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                    ImageDraw.Draw(cap).text((nx, ny), "10", font=fn, fill=PLATA + (255,))
                    mask = Image.new("L", (W, H), 0)
                    ImageDraw.Draw(mask).rectangle([nx - 10, 0, nx + rev, H], fill=255)
                    cap.putalpha(Image.composite(cap.getchannel("A"), Image.new("L", (W, H), 0), mask))
                    capa.alpha_composite(cap)
                    d = ImageDraw.Draw(capa)
                    # plancha
                    px = nx + rev
                    d.rounded_rectangle([px - 60 * s, cyy - 40 * s, px + 90 * s, cyy + 40 * s], radius=int(20 * s), fill=CLARO + (255,))
                    d.rectangle([px - 20 * s, cyy - 70 * s, px + 70 * s, cyy - 40 * s], fill=CLARO + (255,))
                    for k in range(3):
                        d.line([px - 70 * s - k * 22 * s, cyy - 10 * s + k * 10 * s, px - 100 * s - k * 22 * s, cyy - 10 * s + k * 10 * s],
                               fill=TEXTO + (160,), width=int(3 * s))
                    chip(d, W * 0.5, H * 0.16, "NÚMEROS PLATEADOS, DE FÚTBOL AMERICANO, PLANCHADOS", num_a)
        return capa

    _render(dest, W, H, dur, cuadro1 if parte == 1 else cuadro2, fondo)


def corto_subasta(dest, W, H, dur, tiempos, fondo=None):
    """Corto animado de la camiseta: Diego se la cambia a Hodge -> la guarda 36 años -> subasta -> 9 millones.
    tiempos = {"cambio": s, "guardo": s, "subasta": s, "millones": s, "cara": s}."""
    s = W / 1920
    f_e = fuente(500, 26 * s)
    f_lab = fuente(800, 30 * s)
    f_big = fuente(800, 150 * s)
    f_anio = fuente(800, 90 * s)
    xl = 96 * s
    AZUL = (28, 60, 130)
    BLANCO = (235, 235, 235)
    PLATA = (205, 210, 220)
    T = {k: float(v) for k, v in tiempos.items()}
    ruta = RAIZ / "proyectos" / "argentina-1986" / "material" / "retratos" / "caras" / "maradona.png"
    cara = _circulo(_retrato(ruta, int(150 * s)), ACENTO + (255,), 6 * s) if ruta.exists() else None

    def chip(d, cx, y, txt, a, col=ACENTO, f=None):
        f = f or f_lab
        tw = d.textlength(txt, font=f)
        d.rectangle([cx - tw / 2 - 16 * s, y, cx + tw / 2 + 16 * s, y + f.size + 18 * s], fill=col + (int(255 * a),))
        d.text((cx - tw / 2, y + 8 * s), txt, font=f, fill=OSCURO + (int(255 * a),))

    def cuadro(t, i, n):
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        a = ease(t / 0.4)
        _marca(d, s, int(255 * a))
        d.rectangle([xl, 136 * s, xl + 46 * s * a, 140 * s], fill=ACENTO + (int(255 * a),))
        _espaciado(d, (xl + 62 * s, 122 * s), "LA CAMISETA", f_e, ACENTO + (int(255 * a),), 4 * s)
        t_c, t_g, t_s, t_m, t_k = (T.get(k, 1e9) for k in ("cambio", "guardo", "subasta", "millones", "cara"))
        base_y = H * 0.78
        if t < t_g:
            # Diego y Hodge frente a frente; las camisetas se cruzan
            b = ease((t - t_c) / 0.5)
            xd, xh = W * 0.30, W * 0.70
            _persona(d, xd, base_y, 330 * s, ACENTO, 255, ancho=0.26)
            _persona(d, xh, base_y, 360 * s, CLARO, 255, ancho=0.26)
            if cara is not None:
                capa.alpha_composite(cara, (int(xd - 75 * s), int(base_y - 330 * s - 20 * s)))
                d = ImageDraw.Draw(capa)
            chip(d, xd, base_y + 20 * s, "MARADONA", 1.0)
            chip(d, xh, base_y + 20 * s, "STEVE HODGE · EL DEL DESPEJE", 1.0, col=CLARO)
            k = ease((t - t_c - 0.3) / 1.0)
            cy = base_y - 170 * s
            arco = -math.sin(k * math.pi) * 160 * s
            _camiseta(d, xd + (xh - xd) * k, cy + arco, 170 * s, AZUL, numero=10, alpha=255, borde=CLARO, num_color=PLATA)
            _camiseta(d, xh - (xh - xd) * k, cy - arco, 150 * s, BLANCO, numero=18, alpha=255, borde=PANEL, num_color=OSCURO)
            chip(d, W / 2, H * 0.17, "DESPUÉS DEL PARTIDO, EN EL VESTUARIO", b, col=TEXTO)
        elif t < t_s:
            # la camiseta en un marco; los años pasan
            m = t - t_g
            cx, cy = W * 0.32, H * 0.50
            d.rectangle([cx - 190 * s, cy - 210 * s, cx + 190 * s, cy + 210 * s], fill=PANEL + (255,), outline=CLARO + (255,), width=int(8 * s))
            _camiseta(d, cx, cy, 300 * s, AZUL, numero=10, alpha=255, borde=CLARO, num_color=PLATA)
            anio = 1986 + int(min(36, m / 2.2 * 36))
            txt = str(anio)
            tw = d.textlength(txt, font=f_big)
            d.text((W * 0.68 - tw / 2, H * 0.34), txt, font=f_big, fill=TEXTO + (255,))
            yrs = anio - 1986
            chip(d, W * 0.68, H * 0.34 + 180 * s, f"{yrs} AÑOS GUARDADA" if yrs != 1 else "1 AÑO GUARDADA", 1.0)
            # barra de tiempo
            d.line([W * 0.52, H * 0.72, W * 0.84, H * 0.72], fill=VERDE + (255,), width=int(6 * s))
            d.line([W * 0.52, H * 0.72, W * 0.52 + (W * 0.32) * yrs / 36, H * 0.72], fill=ACENTO + (255,), width=int(6 * s))
            chip(d, W / 2, H * 0.17, "HODGE LA GUARDÓ EN SU CASA", ease(m / 0.4), col=TEXTO)
        else:
            m = t - t_s
            # casa de remates: podio, martillo y precio que sube
            cx = W * 0.5
            d.rectangle([cx - 160 * s, H * 0.60, cx + 160 * s, H * 0.72], fill=PANEL + (255,), outline=CLARO + (255,), width=int(4 * s))
            _camiseta(d, cx, H * 0.47, 240 * s, AZUL, numero=10, alpha=255, borde=CLARO, num_color=PLATA)
            # martillo que golpea
            g = (m % 0.8) / 0.8
            ang = -0.9 + 0.9 * (1 - abs(1 - 2 * g)) if t < t_m + 0.5 else -0.2
            mx, my = W * 0.80, H * 0.52
            ex, ey = mx + math.cos(ang) * 140 * s, my + math.sin(ang) * 140 * s
            d.line([mx, my, ex, ey], fill=CLARO + (255,), width=int(14 * s))
            d.rounded_rectangle([ex - 50 * s, ey - 28 * s, ex + 50 * s, ey + 28 * s], radius=int(10 * s), fill=ACENTO + (255,))
            d.rectangle([mx - 90 * s, my + 60 * s, mx + 90 * s, my + 80 * s], fill=CLARO + (255,))
            chip(d, W / 2, H * 0.17, "SOTHEBY'S · LONDRES · MAYO DE 2022", ease(m / 0.4), col=TEXTO)
            if t >= t_m:
                k = ease((t - t_m) / 1.6)
                val = int(9_280_000 * k)
                txt = "US$ " + f"{val:,}".replace(",", ".")
                tw = d.textlength(txt, font=f_anio)
                d.text((cx - tw / 2, H * 0.76), txt, font=f_anio, fill=(ACENTO if k >= 1 else TEXTO) + (255,))
            if t >= t_k:
                chip(d, W / 2, H * 0.88, "LA CAMISETA MÁS CARA DE LA HISTORIA DEL DEPORTE", ease((t - t_k) / 0.4))
        return capa

    _render(dest, W, H, dur, cuadro, fondo)


# ---------- mapa de Malvinas (pedido del usuario, 11/11: "aclaremos qué son las Malvinas") ----------
_SUDAMERICA_SUR = [  # contorno aproximado del cono sur (lon, lat): Argentina, Uruguay y Chile como una sola masa
    (-53.4, -33.7), (-56.0, -34.9), (-58.4, -34.6), (-57.4, -36.3), (-57.5, -38.0), (-62.0, -39.0), (-62.3, -40.6),
    (-65.0, -41.0), (-63.6, -42.3), (-64.6, -42.9), (-65.0, -43.3), (-65.3, -45.0), (-67.5, -45.9), (-65.9, -47.75),
    (-67.7, -49.3), (-68.9, -50.3), (-69.2, -51.6), (-68.4, -52.3), (-69.6, -52.6), (-68.6, -52.7), (-67.7, -53.8),
    (-65.2, -54.6), (-66.5, -55.0), (-68.6, -55.0), (-70.5, -55.2), (-72.5, -54.0), (-74.5, -52.5), (-75.5, -48.5),
    (-74.2, -46.0), (-73.6, -43.0), (-73.4, -39.5), (-73.6, -37.0), (-71.6, -33.0), (-71.4, -28.0), (-71.0, -20.0), (-43.0, -20.0), (-44.0, -23.0),
    (-46.5, -24.0), (-48.5, -26.0), (-48.6, -28.5), (-50.3, -30.5), (-52.1, -32.2), (-53.4, -33.7)]
_MALVINAS = [
    [(-61.3, -51.3), (-60.2, -51.25), (-59.7, -51.6), (-60.0, -52.2), (-60.9, -52.25), (-61.4, -51.8)],   # Gran Malvina
    [(-59.5, -51.35), (-58.3, -51.3), (-57.7, -51.55), (-58.1, -51.9), (-58.7, -52.35), (-59.4, -52.2), (-59.6, -51.75)],  # Soledad
]


def mapa_malvinas(dest, W, H, dur, tiempos, etiqueta="", fondo=None):
    """Mapa del Atlántico Sur: aparece el continente, se marcan las islas, la distancia a la costa y la flecha a
    Londres. tiempos = {"islas": s, "distancia": s, "reino": s, "desde": s} (cada paso entra al nombrarlo)."""
    s = W / 1920
    lon0, lon1, lat0, lat1 = -78.0, -44.0, -27.0, -57.0
    alto_m = H * 0.86
    esc_y = alto_m / (lat0 - lat1)
    esc_x = esc_y * math.cos(math.radians(45))
    ancho_m = (lon1 - lon0) * esc_x
    ox = W * 0.60 - ancho_m / 2
    oy = H * 0.07

    def P(lon, lat):
        return (ox + (lon - lon0) * esc_x, oy + (lat0 - lat) * esc_y)

    f_e = fuente(500, 26 * s)
    f_lab = fuente(800, 34 * s)
    f_chico = fuente(600, 24 * s)
    f_big = fuente(800, 54 * s)
    xl = 96 * s
    T = {k: float(v) for k, v in tiempos.items()}
    cont = [P(*p) for p in _SUDAMERICA_SUR]
    centro_islas = P(-59.4, -51.8)
    islas = [[(centro_islas[0] + (q[0] - centro_islas[0]) * 1.7, centro_islas[1] + (q[1] - centro_islas[1]) * 1.7)
              for q in (P(*p) for p in isla)] for isla in _MALVINAS]  # agrandadas para que se lean
    costa = P(-69.05, -51.0)

    def chip(d, x, y, txt, a, col=ACENTO, f=None, centro=False):
        f = f or f_lab
        tw = d.textlength(txt, font=f)
        if centro:
            x -= tw / 2 + 16 * s
        d.rectangle([x, y, x + tw + 32 * s, y + f.size + 18 * s], fill=col + (int(255 * a),))
        d.text((x + 16 * s, y + 8 * s), txt, font=f, fill=OSCURO + (int(255 * a),))

    def cuadro(t, i, n):
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        a = ease(t / 0.6)
        # mar
        d.rectangle([0, 0, W, H], fill=(10, 22, 30, int(200 * a)))
        for k in range(0, int(W), int(60 * s)):  # retícula de coordenadas
            d.line([k, 0, k, H], fill=(30, 50, 60, int(120 * a)), width=1)
        for k in range(0, int(H), int(60 * s)):
            d.line([0, k, W, k], fill=(30, 50, 60, int(120 * a)), width=1)
        # continente
        d.polygon(cont, fill=PANEL + (int(255 * a),), outline=VERDE + (int(255 * a),))
        f_pais = fuente(800, 44 * s)
        x, y = P(-67.0, -38.5)
        _espaciado(d, (x, y), "ARGENTINA", f_pais, CLARO + (int(200 * a),), 10 * s)
        x, y = P(-55.0, -45.0)
        _espaciado(d, (x, y), "OCÉANO ATLÁNTICO", f_chico, (90, 130, 140, int(220 * a)), 8 * s)
        _marca(d, s, int(255 * a))
        if etiqueta:
            d.rectangle([xl, 136 * s, xl + 46 * s * a, 140 * s], fill=ACENTO + (int(255 * a),))
            _espaciado(d, (xl + 62 * s, 122 * s), etiqueta.upper(), f_e, ACENTO + (int(255 * a),), 4 * s)
        # islas
        ti = T.get("islas", 0.8)
        if t >= ti:
            b = ease((t - ti) / 0.5)
            puls = 0.5 + 0.5 * math.sin((t - ti) * 4)
            r = (60 + 30 * puls) * s
            d.ellipse([centro_islas[0] - r, centro_islas[1] - r, centro_islas[0] + r, centro_islas[1] + r],
                      outline=ACENTO + (int(160 * b * (1 - puls * 0.5)),), width=int(3 * s))
            for isla in islas:
                d.polygon(isla, fill=ACENTO + (int(255 * b),))
            chip(d, centro_islas[0] + 90 * s, centro_islas[1] + 40 * s, "ISLAS MALVINAS", b)
            d.line([centro_islas[0] + 40 * s, centro_islas[1] + 20 * s, centro_islas[0] + 90 * s, centro_islas[1] + 56 * s],
                   fill=ACENTO + (int(255 * b),), width=int(3 * s))
        # distancia a la costa
        td = T.get("distancia", 1e9)
        if t >= td:
            b = ease((t - td) / 0.8)
            x0, y0 = costa[0] + 4 * s, costa[1]
            x1, y1 = centro_islas[0] - 60 * s, centro_islas[1] - 5 * s
            xe = x0 + (x1 - x0) * b
            ye = y0 + (y1 - y0) * b
            k = 0
            while True:  # línea punteada
                fx = k * 18 * s / max(1, math.hypot(x1 - x0, y1 - y0))
                if fx > b:
                    break
                xa, ya = x0 + (x1 - x0) * fx, y0 + (y1 - y0) * fx
                fb = min(b, fx + 10 * s / max(1, math.hypot(x1 - x0, y1 - y0)))
                d.line([xa, ya, x0 + (x1 - x0) * fb, y0 + (y1 - y0) * fb], fill=TEXTO + (255,), width=int(4 * s))
                k += 1
            if b >= 1:
                chip(d, (x0 + x1) / 2, y0 - 80 * s, "≈ 500 KM", ease((t - td - 0.8) / 0.3), col=TEXTO, f=f_lab, centro=True)
        # flecha al Reino Unido
        tr = T.get("reino", 1e9)
        if t >= tr:
            b = ease((t - tr) / 0.9)
            x0, y0 = centro_islas[0] + 40 * s, centro_islas[1] - 40 * s
            x1, y1 = W - 120 * s, 120 * s
            xe, ye = x0 + (x1 - x0) * b, y0 + (y1 - y0) * b
            d.line([x0, y0, xe, ye], fill=(200, 80, 80, 255), width=int(5 * s))
            ang = math.atan2(y1 - y0, x1 - x0)
            pa = [(xe, ye), (xe - 26 * s * math.cos(ang - 0.45), ye - 26 * s * math.sin(ang - 0.45)),
                  (xe - 26 * s * math.cos(ang + 0.45), ye - 26 * s * math.sin(ang + 0.45))]
            d.polygon(pa, fill=(200, 80, 80, 255))
            if b >= 1:
                c = ease((t - tr - 0.9) / 0.3)
                tw = d.textlength("REINO UNIDO", font=f_lab)
                chip(d, W - 140 * s - tw, 150 * s, "REINO UNIDO", c, col=(220, 120, 120))
                d.text((W - 140 * s - d.textlength("A 12.700 KM", font=f_chico) + 32 * s, 220 * s), "A 12.700 KM",
                       font=f_chico, fill=TEXTO + (int(255 * c),))
        # desde 1833
        tdd = T.get("desde", 1e9)
        if t >= tdd:
            b = ease((t - tdd) / 0.4)
            d.text((xl, H - 260 * s), "1833", font=fuente(800, 120 * s), fill=TEXTO + (int(255 * b),))
            chip(d, xl, H - 120 * s, "OCUPADAS POR INGLATERRA · RECLAMADAS POR ARGENTINA", b)
        return capa

    _render(dest, W, H, dur, cuadro, fondo)


# ---------- zócalo (PNG transparente que se superpone a una foto o video) ----------
def zocalo(dest, W, H, titulo, sub=""):
    """Nombre en caja clara (mono bold, letra oscura) y bajada en caja oscura; barra verde a la izquierda."""
    s = W / 1920
    f_t = fuente(700, 50 * s)
    f_s = fuente(500, 26 * s)
    esp = 2 * s
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    T = titulo.upper()
    x = 96 * s
    h_t, h_s = 78 * s, 54 * s
    y = H - 150 * s - (h_s if sub else 0)
    wt = d.textlength(T, font=f_t) + 52 * s
    d.rectangle([x, y, x + 8 * s, y + h_t + (h_s if sub else 0)], fill=ACENTO + (255,))
    d.rectangle([x + 8 * s, y, x + 8 * s + wt, y + h_t], fill=CLARO + (255,))
    d.text((x + 34 * s, y + 13 * s), T, font=f_t, fill=FONDO + (255,))
    if sub:
        ws = _ancho_esp(sub, f_s, esp) + 52 * s
        d.rectangle([x + 8 * s, y + h_t, x + 8 * s + ws, y + h_t + h_s], fill=OSCURO + (220,))
        _espaciado(d, (x + 34 * s, y + h_t + 11 * s), sub, f_s, CLARO + (255,), esp)
    img.save(dest)


def golpe(src, dest, W, H, dur, texto, sub="", t0=0.5, local="", visitante=""):
    """Marcador gigante que GOLPEA sobre un clip ya renderizado (src, WxH) en el segundo t0:
    entra grande y cae a su tamaño, flash blanco, sacudón, y el video se oscurece detrás.
    texto = "1-0"; local/visitante a los costados; sub abajo (ej. "MALDINI · 1'")."""
    s = W / 1920
    f_g = fuente(800, 330 * s)
    f_eq = fuente(700, 58 * s)
    f_sub = fuente(700, 40 * s)
    n = round(dur * FPS)
    txt = texto
    L, V = local.upper(), visitante.upper()
    d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    wg = d0.textlength(txt, font=f_g)
    bb = d0.textbbox((0, 0), txt, font=f_g)
    hg = bb[3] - bb[1]
    sep = 56 * s
    # capa del marcador a tamaño final (se escala para el golpe)
    wl = d0.textlength(L, font=f_eq) if L else 0
    wv = d0.textlength(V, font=f_eq) if V else 0
    ancho = int(wl + wv + wg + 2 * sep + 40 * s)
    alto = int(hg + 140 * s)
    capa = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    yg = (alto - hg) / 2 - bb[1] - 30 * s
    xg = wl + sep + 20 * s
    for dx, dy in ((6, 8), (3, 4)):  # sombra
        d.text((xg + dx * s, yg + dy * s), txt, font=f_g, fill=(0, 0, 0, 150))
    d.text((xg, yg), txt, font=f_g, fill=TEXTO + (255,))
    ym = (alto - 30 * s) / 2 - 30 * s
    if L:
        d.text((20 * s, ym), L, font=f_eq, fill=TEXTO + (255,))
        d.rectangle([20 * s, ym + 76 * s, 20 * s + wl, ym + 84 * s], fill=COLOR_EQUIPO.get(L, ACENTO) + (255,))
    if V:
        xv = xg + wg + sep
        d.text((xv, ym), V, font=f_eq, fill=TEXTO + (255,))
        d.rectangle([xv, ym + 76 * s, xv + wv, ym + 84 * s], fill=COLOR_EQUIPO.get(V, ACENTO) + (255,))
    if ancho > 0.88 * W:  # palabras largas ("SHEVCHENKO"): achicar para que entre en el cuadro
        k = 0.88 * W / ancho
        ancho, alto = int(ancho * k), int(alto * k)
        capa = capa.resize((ancho, alto), Image.LANCZOS)

    p_in =subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(src), "-frames:v", str(n), "-f", "rawvideo",
                             "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    p = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", "-an", str(dest)], stdin=subprocess.PIPE)
    import math
    tam = W * H * 3
    ultimo = Image.new("RGB", (W, H))
    for i in range(n):
        buf = p_in.stdout.read(tam)
        if len(buf) == tam:
            ultimo = Image.frombytes("RGB", (W, H), buf)
        t = i / FPS - t0
        img = ultimo.convert("RGBA")
        if t >= 0:
            oscuro = Image.new("RGBA", (W, H), OSCURO + (int(150 * ease(t / 0.15)),))
            img = Image.alpha_composite(img, oscuro)
            esc = 1 + 0.9 * (1 - ease(t / 0.14))          # cae desde grande
            sac = 16 * s * max(0.0, 1 - t / 0.35) * math.sin(t * 90)  # sacudón
            c = capa if esc == 1 else capa.resize((int(ancho * esc), int(alto * esc)), Image.BILINEAR)
            if t < 0.14:
                c.putalpha(c.getchannel("A").point(lambda a: int(a * ease(t / 0.08))))
            img.alpha_composite(c, (int(W / 2 - c.width / 2 + sac), int(H / 2 - c.height / 2 - 20 * s)))
            if sub and t > 0.25:
                a = ease((t - 0.25) / 0.25)
                cs = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                dd = ImageDraw.Draw(cs)
                w = dd.textlength(sub, font=f_sub) + 48 * s
                y = H / 2 + alto / 2 - 10 * s + (1 - a) * 20 * s
                dd.rectangle([W / 2 - w / 2, y, W / 2 + w / 2, y + 66 * s], fill=ACENTO + (int(255 * a),))
                dd.text((W / 2 - w / 2 + 24 * s, y + 10 * s), sub, font=f_sub, fill=OSCURO + (int(255 * a),))
                img = Image.alpha_composite(img, cs)
            flash = int(200 * max(0.0, 1 - t / 0.18))
            if flash:
                img = Image.alpha_composite(img, Image.new("RGBA", (W, H), (255, 255, 255, flash)))
        p.stdin.write(img.convert("RGB").tobytes())
    p_in.stdout.close()
    p_in.wait()
    p.stdin.close()
    if p.wait() != 0:
        raise SystemExit(f"ffmpeg falló renderizando {dest}")


def _icono(d, kind, cx, cy, r, color):
    """Íconos simples dibujados: 'mas' (suscribirse), 'like' (pulgar), 'comentario' (globito), 'check'."""
    w = max(2, int(r * 0.16))
    if kind == "mas":
        d.line([cx - r * 0.55, cy, cx + r * 0.55, cy], fill=color, width=w)
        d.line([cx, cy - r * 0.55, cx, cy + r * 0.55], fill=color, width=w)
    elif kind == "check":
        d.line([cx - r * 0.55, cy, cx - r * 0.12, cy + r * 0.45, cx + r * 0.6, cy - r * 0.45], fill=color, width=w,
               joint="curve")
    elif kind == "like":
        d.rounded_rectangle([cx - r * 0.75, cy - r * 0.05, cx - r * 0.42, cy + r * 0.7], r * 0.08, fill=color)
        d.rounded_rectangle([cx - r * 0.32, cy - r * 0.1, cx + r * 0.72, cy + r * 0.7], r * 0.2, fill=color)
        d.polygon([(cx - r * 0.32, cy - r * 0.05), (cx - r * 0.05, cy - r * 0.75), (cx + r * 0.2, cy - r * 0.7),
                   (cx + r * 0.12, cy - r * 0.1)], fill=color)
    elif kind == "comentario":
        d.rounded_rectangle([cx - r * 0.75, cy - r * 0.6, cx + r * 0.75, cy + r * 0.35], r * 0.25, fill=color)
        d.polygon([(cx - r * 0.35, cy + r * 0.3), (cx - r * 0.5, cy + r * 0.75), (cx + r * 0.05, cy + r * 0.3)], fill=color)


def cierre(dest, W, H, dur, botones, titulo="LOS 11", sub="", fondo=None):
    """Pantalla final: botones que entran de a uno (t = segundo en que el narrador los nombra).
    botones = [{"texto": "SUSCRIBITE", "icono": "mas", "t": 1.2, "click": "SUSCRIPTO"}, ...]
    El que tiene "click" recibe un cursor que lo aprieta y cambia de texto. Abajo queda lugar libre
    para los elementos de la pantalla final de YouTube."""
    import math
    s = W / 1920
    f_b = fuente(800, 64 * s)
    f_t = fuente(800, 120 * s)
    f_s = fuente(500, 40 * s, plex=True)
    d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    hb, r_ic, pad, gap = 150 * s, 42 * s, 44 * s, 48 * s
    anchos = [pad * 2 + r_ic * 2 + 22 * s + max(d0.textlength(b["texto"], font=f_b),
                                                 d0.textlength(b.get("click", ""), font=f_b)) for b in botones]
    total = sum(anchos) + gap * (len(botones) - 1)
    yb = H / 2 - 20 * s

    def cuadro(t, i, n):
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        a = ease(t / 0.5)
        al = int(255 * a)
        _marca(d, s, al)
        # título arriba
        tt = titulo.split(" ")
        x = W / 2 - d0.textlength(titulo, font=f_t) / 2
        y = yb - 220 * s + (1 - a) * 30 * s
        for k, palabra in enumerate(tt):
            col = ACENTO if palabra.isdigit() else TEXTO
            d.text((x, y), palabra, font=f_t, fill=col + (al,))
            x += d0.textlength(palabra + " ", font=f_t)
        x = W / 2 - total / 2
        for b, wb in zip(botones, anchos):
            tb = t - b["t"]
            if tb > 0:
                e = ease(tb / 0.3)
                pop = 1 + 0.25 * math.sin(min(1.0, tb / 0.3) * math.pi)  # entra con rebote
                clic_t = b["t"] + 0.9
                apretado = b.get("click") and t >= clic_t
                presion = 0.92 if b.get("click") and clic_t - 0.08 <= t < clic_t + 0.08 else 1.0
                esc = pop * presion
                cx, cy = x + wb / 2, yb + hb / 2
                w2, h2 = wb * esc / 2, hb * esc / 2
                fondo_b = (PANEL if apretado else ACENTO) + (int(255 * e),)
                d.rounded_rectangle([cx - w2, cy - h2, cx + w2, cy + h2], h2, fill=fondo_b)
                txt = b["click"] if apretado else b["texto"]
                col = TEXTO if apretado else OSCURO
                ic = "check" if apretado else b.get("icono", "mas")
                icx = cx - w2 + pad * esc + r_ic * esc
                _icono(d, ic, icx, cy, r_ic * esc, col + (int(255 * e),))
                fb = fuente(800, 64 * s * esc)
                d.text((icx + r_ic * esc + 22 * s * esc, cy - 42 * s * esc), txt, font=fb, fill=col + (int(255 * e),))
                if apretado:  # onda del clic
                    k = (t - clic_t) / 0.6
                    if k < 1:
                        rr = h2 * (1 + 0.6 * k)
                        d.rounded_rectangle([cx - w2 - (rr - h2), cy - rr, cx + w2 + (rr - h2), cy + rr], rr,
                                            outline=ACENTO + (int(200 * (1 - k)),), width=int(4 * s))
                # cursor que viene a apretar
                if b.get("click") and clic_t - 0.7 <= t < clic_t + 0.5:
                    k = ease((t - (clic_t - 0.7)) / 0.6)
                    px = cx + w2 * 0.4 + (1 - k) * 260 * s
                    py = cy + (1 - k) * 200 * s
                    flecha = [(0, 0), (0, 44), (11, 34), (19, 52), (27, 48), (19, 31), (34, 31)]
                    pts = [(px + u * s * 1.3, py + v * s * 1.3) for u, v in flecha]
                    d.polygon(pts, fill=TEXTO + (255,), outline=OSCURO + (255,))
            x += wb + gap
        if sub:
            tl = max(b["t"] for b in botones) + 0.6
            if t > tl:
                e = ease((t - tl) / 0.5)
                w = d0.textlength(sub, font=f_s)
                d.text((W / 2 - w / 2, yb + hb + 70 * s + (1 - e) * 16 * s), sub, font=f_s, fill=CLARO + (int(255 * e),))
        return capa

    _render(dest, W, H, dur, cuadro, fondo)


def prestamo(dest, W, H, dur, foto, nombre, origen, destino, t_mov=0.8, t_nota=None, nota="", sub_nota="",
             etiqueta="", fondo=None):
    """Jugador a préstamo: su retrato viaja del club dueño (origen) al club donde juega (destino) por una flecha
    punteada con el cartel 'A PRÉSTAMO'. En t_nota cae un sello sobre el club de origen (nota/sub_nota).
    origen/destino = {"nombre": "Chelsea", "colores": [[3, 70, 148]]} (uno o más colores, se hacen rayas)."""
    import math
    s = W / 1920
    r = 130 * s
    f_club = fuente(800, 64 * s)
    f_e = fuente(500, 26 * s)
    f_lab = fuente(700, 32 * s)
    f_nom = fuente(700, 44 * s)
    f_sello = fuente(800, 40 * s)
    f_ss = fuente(600, 26 * s)
    cara = _circulo(_retrato(foto, 2 * r)) if foto else None
    xo, xd, yp = W * 0.24, W * 0.76, H * 0.66
    pw, ph = 470 * s, 150 * s
    xl = 96 * s

    def panel(d, cx, club, a):
        al = int(255 * a)
        d.rounded_rectangle([cx - pw / 2, yp - ph / 2, cx + pw / 2, yp + ph / 2], 14 * s, fill=PANEL + (int(235 * a),))
        cols = [tuple(c) for c in club.get("colores", [ACENTO])]
        n = 8
        for k in range(n):  # franja con los colores del club
            x0 = cx - pw / 2 + k * pw / n
            d.rectangle([x0, yp + ph / 2 - 14 * s, x0 + pw / n, yp + ph / 2], fill=cols[k % len(cols)] + (al,))
        tw = d.textlength(club["nombre"].upper(), font=f_club)
        d.text((cx - tw / 2, yp - 46 * s), club["nombre"].upper(), font=f_club, fill=TEXTO + (al,))

    def pos(k):  # recorrido en arco de origen a destino
        x = xo + (xd - xo) * k
        y = yp - ph / 2 - r - 40 * s - math.sin(math.pi * k) * 150 * s
        return x, y

    def cuadro(t, i, n):
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        a = ease(t / 0.4)
        _marca(d, s, int(255 * a))
        if etiqueta:
            d.rectangle([xl, 196 * s, xl + 46 * s * a, 200 * s], fill=ACENTO + (int(255 * a),))
            _espaciado(d, (xl + 62 * s, 182 * s), etiqueta.upper(), f_e, ACENTO + (int(255 * a),), 4 * s)
        panel(d, xo, origen, ease((t - 0.1) / 0.4))
        panel(d, xd, destino, ease((t - 0.3) / 0.4))
        m = ease((t - t_mov) / 1.1)
        # flecha punteada que se dibuja delante del jugador
        if t > t_mov - 0.3:
            b = ease((t - (t_mov - 0.3)) / 0.3)
            pasos = 40
            for k in range(pasos):
                k0, k1 = k / pasos, (k + 0.5) / pasos
                if k0 > max(m, 0.02) + 0.98 * b * (1 - m) and m < 1:
                    pass
                p0, p1 = pos(k0), pos(k1)
                d.line([p0, p1], fill=ACENTO + (int(200 * b),), width=max(2, int(5 * s)))
            hx, hy = pos(1.0)
            fl = 22 * s
            d.polygon([(hx, hy + r + 4 * s), (hx - fl, hy + r - fl * 1.4), (hx + fl, hy + r - fl * 1.4)],
                      fill=ACENTO + (int(255 * b),))
            lab = "A PRÉSTAMO"
            tw = _ancho_esp(lab, f_lab, 6 * s)
            mx, my = pos(0.5)
            d.rounded_rectangle([mx - tw / 2 - 22 * s, my - 150 * s, mx + tw / 2 + 22 * s, my - 92 * s], 10 * s,
                                fill=ACENTO + (int(255 * b),))
            _espaciado(d, (mx - tw / 2, my - 140 * s), lab, f_lab, OSCURO + (int(255 * b),), 6 * s)
        # jugador
        ap = ease((t - 0.35) / 0.4)
        x, y = pos(max(0.0, m))
        if cara is not None and ap > 0:
            c = cara.copy()
            c.putalpha(c.getchannel("A").point(lambda v: int(v * ap)))
            capa.alpha_composite(c, (int(x - r), int(y - r)))
            d.ellipse([x - r, y - r, x + r, y + r], outline=ACENTO + (int(255 * ap),), width=max(4, int(7 * s)))
            tw = d.textlength(nombre.upper(), font=f_nom)
            d.text((x - tw / 2, y - r - 62 * s), nombre.upper(), font=f_nom, fill=TEXTO + (int(255 * ap),))
        # sello sobre el club de origen
        if t_nota is not None and t >= t_nota and nota:
            k = (t - t_nota) / 0.25
            esc = 1 + 0.8 * (1 - ease(k))
            al = int(255 * ease(k / 0.6))
            ancho = max(d.textlength(nota.upper(), font=f_sello), d.textlength(sub_nota.upper(), font=f_ss)) + 60 * s
            lay = Image.new("RGBA", (int(ancho), int(130 * s)), (0, 0, 0, 0))
            dl = ImageDraw.Draw(lay)
            rojo = (200, 16, 46)
            dl.rounded_rectangle([4, 4, lay.width - 4, lay.height - 4], 12 * s, outline=rojo + (255,), width=int(6 * s),
                                 fill=(14, 26, 14, 200))
            tw = dl.textlength(nota.upper(), font=f_sello)
            dl.text((lay.width / 2 - tw / 2, 18 * s), nota.upper(), font=f_sello, fill=(255, 90, 100, 255))
            if sub_nota:
                tw = dl.textlength(sub_nota.upper(), font=f_ss)
                dl.text((lay.width / 2 - tw / 2, 78 * s), sub_nota.upper(), font=f_ss, fill=TEXTO + (255,))
            lay = lay.rotate(-8, expand=True, resample=Image.BICUBIC)
            lay = lay.resize((int(lay.width * esc), int(lay.height * esc)), Image.BILINEAR)
            lay.putalpha(lay.getchannel("A").point(lambda v: int(v * al / 255)))
            capa.alpha_composite(lay, (int(xo - lay.width / 2), int(yp + ph / 2 + 30 * s)))
        return capa

    _render(dest, W, H, dur, cuadro, fondo)
