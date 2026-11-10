"""Gráficos del canal dibujados con Pillow: intro animada, marcador, placas de texto y zócalos.

Estilo del canal (manual de estilo, 05/11): tipografía "Técnica" (JetBrains Mono para títulos, nombres y
números; IBM Plex Sans para texto descriptivo) y paleta "Forest". Placas y marcador van SOBRE VIDEO:
un tramo del partido desenfocado, oscurecido y teñido de verde (sin logos de canal: el UEFA se recorta),
nunca sobre negro liso. Cuando se nombra a alguien, va su retrato (`foto`); `formacion` arma el equipo en la cancha.

Las animaciones se renderizan cuadro a cuadro y se mandan a ffmpeg por pipe.
"""
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
