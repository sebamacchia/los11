"""Collage tipo recorte de papel (paper cut): fotos con borde blanco rasgado, cinta, sombra, papelitos
escritos a máquina y marcador rojo, que se pegan sobre un cartón negro al ritmo de la narración.

Las piezas NO hacen zoom (regla del canal): entran deslizándose unos píxeles y "caen" (la sombra se achica),
y tiemblan 1 px cada 2 cuadros como stop-motion.

Prueba: /usr/bin/python3 herramientas/collage.py proyectos/argentina-1986/collage_prueba.json
"""
import json
import math
import random
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

RAIZ = Path(__file__).resolve().parent.parent
FUENTES = RAIZ / "animaciones" / "futbol" / "assets" / "fonts"
W, H, FPS = 1920, 1080, 30
PAPEL = (240, 236, 224)
SOBRIO = False  # "estilo": "sobrio" en el json: sin bordes, sin cinta, sin rotar, cortes secos, texto liso
ROJO = (214, 40, 32)


def fuente(tam, mono=True, peso=700):
    f = ImageFont.truetype(str(FUENTES / ("jetbrains-mono.ttf" if mono else "plex-sans.ttf")), tam)
    try:
        f.set_variation_by_axes([peso])
    except Exception:
        pass
    return f


def fondo(seed=1):
    """Cartón negro con grano y fibras."""
    rnd = random.Random(seed)
    base = Image.new("RGB", (W, H), (24, 24, 22))
    grano = Image.effect_noise((W, H), 28).convert("L")
    base = Image.composite(Image.new("RGB", (W, H), (40, 39, 36)), base, grano.point(lambda v: max(0, v - 120)))
    d = ImageDraw.Draw(base)
    for _ in range(900):  # fibras
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        a, l = rnd.uniform(0, math.pi), rnd.uniform(4, 18)
        c = rnd.randint(30, 48)
        d.line([(x, y), (x + l * math.cos(a), y + l * math.sin(a))], fill=(c, c, c - 2), width=1)
    # viñeta
    v = Image.new("L", (W, H), 0)
    ImageDraw.Draw(v).ellipse([-W * 0.25, -H * 0.35, W * 1.25, H * 1.35], fill=255)
    v = v.filter(ImageFilter.GaussianBlur(160))
    return Image.composite(base, Image.new("RGB", (W, H), (8, 8, 8)), v)


def rasgado(w, h, rnd, fino=5, salto=7):
    """Máscara de un rectángulo con borde rasgado."""
    pts = []
    for (x0, y0, x1, y1) in [(0, 0, w, 0), (w, 0, w, h), (w, h, 0, h), (0, h, 0, 0)]:
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) / salto))
        for i in range(n):
            t = i / n
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            # hacia adentro
            nx, ny = (y1 - y0), -(x1 - x0)
            ln = math.hypot(nx, ny) or 1
            off = rnd.uniform(0, fino)
            pts.append((x - nx / ln * off, y - ny / ln * off))
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m


def cinta(rnd, ancho=150):
    w, h = ancho, 46
    m = rasgado(w, h, rnd, fino=3, salto=5)
    t = Image.new("RGBA", (w, h), (226, 214, 176, 0))
    t.putalpha(m.point(lambda v: v * 150 // 255))
    return t


def con_sombra(im, rnd, rot):
    """RGBA pieza rotada + sombra aparte (para animar la caída)."""
    im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    a = im.getchannel("A")
    pad = 60
    sombra = Image.new("L", (im.width + pad * 2, im.height + pad * 2), 0)
    sombra.paste(a, (pad, pad))
    sombra = sombra.filter(ImageFilter.GaussianBlur(14)).point(lambda v: v * 170 // 255)
    return im, sombra, pad


def foto(p, rnd):
    src = Image.open(RAIZ / p["archivo"]).convert("RGB")
    if "recorte" in p:
        src = src.crop(p["recorte"])
    if p.get("bn"):
        src = ImageOps.grayscale(src).convert("RGB")
    if "celda" in p:
        cw, ch = p["celda"][2], p["celda"][3]
        src = ImageOps.fit(src, (cw, ch), Image.LANCZOS, centering=p.get("centro", (0.5, 0.5)))
    else:
        alto = p.get("alto", 520)
        src = src.resize((max(1, int(src.width * alto / src.height)), alto), Image.LANCZOS)
    if SOBRIO:
        src = ImageChops.multiply(src, Image.merge("RGB", [Image.effect_noise(src.size, 10).point(lambda v: 215 + v // 6)] * 3))
        return src.convert("RGBA")
    # grano de impresión leve
    src = ImageChops.multiply(src, Image.merge("RGB", [Image.effect_noise(src.size, 10).point(lambda v: 205 + v // 5)] * 3))
    borde = p.get("borde", 18)
    w, h = src.width + borde * 2, src.height + borde * 2
    hoja = Image.new("RGBA", (w, h), PAPEL + (255,))
    hoja.paste(src, (borde, borde))
    hoja.putalpha(rasgado(w, h, rnd))
    if p.get("cinta", True):
        tmp = Image.new("RGBA", (w, h + 30), (0, 0, 0, 0))
        tmp.alpha_composite(hoja, (0, 30))
        for cx in ([0.5] if w < 600 else [0.2, 0.8]):
            c = cinta(rnd).rotate(rnd.uniform(-8, 8), expand=True, resample=Image.BICUBIC)
            tmp.alpha_composite(c, (int(w * cx - c.width / 2), 8))
        hoja = tmp
    return hoja


def papelito(p, rnd):
    """Tira de papel con texto a máquina (JetBrains Mono). "sello": True -> sello rojo."""
    lineas = p["texto"].split("\n")
    if SOBRIO:
        f = fuente(p.get("tam", 34), mono=False, peso=p.get("peso", 450))
        asc, desc = f.getmetrics()
        lh = int((asc + desc) * 1.15)
        w = int(max(f.getlength(l) for l in lineas)) + 4
        im = Image.new("RGBA", (w, lh * len(lineas)), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        for i, l in enumerate(lineas):
            d.text((0, i * lh), l, font=f, fill=(236, 233, 226, 255) if i == 0 else (150, 147, 140, 255))
        return im
    f = fuente(p.get("tam", 40), peso=p.get("peso", 600))
    asc, desc = f.getmetrics()
    lh = asc + desc + 8
    tw = max(f.getlength(l) for l in lineas)
    pad = 26
    w, h = int(tw + pad * 2), int(lh * len(lineas) + pad * 2 - 8)
    if p.get("sello"):
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rectangle([3, 3, w - 4, h - 4], outline=ROJO + (255,), width=6)
        for i, l in enumerate(lineas):
            d.text((pad, pad + i * lh), l, font=f, fill=ROJO + (255,))
        # tinta gastada
        gasto = Image.effect_noise((w, h), 60).point(lambda v: 255 if v > 95 else 90)
        im.putalpha(ImageChops.multiply(im.getchannel("A"), gasto))
        return im
    im = Image.new("RGBA", (w, h), PAPEL + (255,))
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lineas):
        d.text((pad + rnd.uniform(-1, 1), pad + i * lh), l, font=f, fill=(28, 26, 24, 255))
    im.putalpha(rasgado(w, h, rnd, fino=4, salto=6))
    return im


def circulo(p):
    """Círculo de marcador rojo que se dibuja de a poco: devuelve función (progreso 0..1) -> RGBA."""
    w, h = p["ancho"], p["alto"]
    rnd = random.Random(p.get("seed", 3))
    pts = []
    vueltas = 1.12
    n = 220
    for i in range(n + 1):
        a = -math.pi * 0.6 + 2 * math.pi * vueltas * i / n
        r = 1 + 0.04 * math.sin(i / 9) + rnd.uniform(-0.006, 0.006)
        pts.append((w / 2 + (w / 2 - 14) * r * math.cos(a), h / 2 + (h / 2 - 14) * r * math.sin(a)))

    def dibujar(prog):
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        k = max(2, int(len(pts) * min(1, prog)))
        ImageDraw.Draw(im).line(pts[:k], fill=ROJO + (235,), width=11, joint="curve")
        return im
    return dibujar


def flecha(p):
    """Flecha de marcador rojo de "desde" a "hasta" (coordenadas de pantalla), con una leve curva."""
    (x0, y0), (x1, y1) = p["desde"], p["hasta"]
    mx, my = (x0 + x1) / 2 + (y1 - y0) * 0.15, (y0 + y1) / 2 - (x1 - x0) * 0.15
    pts = [((1 - t) ** 2 * x0 + 2 * (1 - t) * t * mx + t * t * x1, (1 - t) ** 2 * y0 + 2 * (1 - t) * t * my + t * t * y1)
           for t in [i / 60 for i in range(61)]]
    ang = math.atan2(y1 - pts[-4][1], x1 - pts[-4][0])
    punta = [(x1 + 34 * math.cos(ang + s), y1 + 34 * math.sin(ang + s)) for s in (math.pi * 0.82, -math.pi * 0.82)]

    def dibujar(prog):
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        k = max(2, int(len(pts) * min(1, prog / 0.8)))
        d.line(pts[:k], fill=ROJO + (235,), width=10, joint="curve")
        if prog >= 0.8:
            for q in punta[:1 if prog < 0.9 else 2]:
                d.line([(x1, y1), q], fill=ROJO + (235,), width=10)
        return im
    return dibujar


def marco(p):
    x, y, w, h = p["caja"]

    def dibujar(prog):
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(im).rectangle([x, y, x + w, y + h], outline=(236, 233, 226, 255), width=p.get("grosor", 3))
        return im
    return dibujar


def momento(texto, retardo, d_voz, valor):
    if isinstance(valor, str) and valor.startswith("@"):
        pos = texto.find(valor[1:])
        if pos < 0:
            raise SystemExit(f"No encuentro '{valor[1:]}'")
        return retardo + d_voz * pos / max(1, len(texto))
    return float(valor)


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def render(cfg, salida):
    texto, retardo, d_voz = cfg["texto"], cfg["retardo"], cfg["d_voz"]
    dur = cfg["duracion"]
    base = Image.new("RGB", (W, H), (9, 9, 9)) if SOBRIO else fondo()
    piezas = []
    for k, p in enumerate(cfg["piezas"]):
        rnd = random.Random(100 + k)
        t0 = momento(texto, retardo, d_voz, p["en"])
        t1 = momento(texto, retardo, d_voz, p["sale"]) if "sale" in p else None
        if p["tipo"] in ("circulo", "flecha", "marco"):
            f = {"circulo": circulo, "flecha": flecha, "marco": marco}[p["tipo"]](p)
            xy = (p["x"], p["y"]) if p["tipo"] == "circulo" else (0, 0)
            piezas.append({"k": "circulo", "t0": t0, "t1": t1, "f": f, "x": xy[0], "y": xy[1],
                           "dur": p.get("dibujo", 0.7)})
            continue
        im = foto(p, rnd) if p["tipo"] == "foto" else papelito(p, rnd)
        im, sombra, pad = con_sombra(im, rnd, 0 if SOBRIO else p.get("rot", rnd.uniform(-4, 4)))
        ang = rnd.uniform(0, 2 * math.pi)
        if "celda" in p:
            px, py = p["celda"][0], p["celda"][1]
        elif SOBRIO or p.get("ancla") == "izq":  # texto y fotos sobrias: x, y = esquina superior izquierda
            px, py = p["x"], p["y"]
        else:
            px, py = int(p["x"] - im.width / 2), int(p["y"] - im.height / 2)
        piezas.append({"k": "pieza", "t0": t0, "t1": t1, "im": im, "sombra": sombra, "pad": pad,
                       "x": px, "y": py, "foto": p["tipo"] == "foto",
                       "dx": math.cos(ang) * 70, "dy": math.sin(ang) * 50 - 30})
    sfx = [pz["t0"] for pz in piezas if pz["k"] == "pieza" and (pz["foto"] or not SOBRIO)]
    n = int(dur * FPS)
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                             "-pix_fmt", "yuv420p", str(salida)], stdin=subprocess.PIPE)
    ultimo = None
    for fi in range(n):
        paso = fi // 2  # stop-motion "en dos": cada cuadro nuevo dura 2
        if SOBRIO:
            paso = fi / 2
        if fi % 2 and ultimo is not None and not SOBRIO:
            proc.stdin.write(ultimo)
            continue
        t = paso * 2 / FPS
        lienzo = base.copy().convert("RGBA")
        for j, pz in enumerate(piezas):
            if t < pz["t0"]:
                continue
            if pz["k"] == "circulo":
                if pz["t1"] is not None and t >= pz["t1"]:
                    continue
                lienzo.alpha_composite(pz["f"]((t - pz["t0"]) / pz["dur"]), (pz["x"], pz["y"]))
                continue
            if SOBRIO:  # corte seco: aparece y desaparece, sin movimiento ni sombra
                if pz["t1"] is None or t < pz["t1"]:
                    lienzo.alpha_composite(pz["im"], (pz["x"], pz["y"]))
                continue
            e = ease((t - pz["t0"]) / 0.22)
            ox, oy = pz["dx"] * (1 - e), pz["dy"] * (1 - e)
            if pz["t1"] is not None and t >= pz["t1"]:  # se va: barrido hacia abajo
                s = ease((t - pz["t1"]) / 0.3)
                if s >= 1:
                    continue
                oy += s * 900
                ox += s * (pz["dx"] * 3)
            jr = random.Random(paso * 31 + j)
            jx, jy = jr.choice((-1, 0, 1)), jr.choice((-1, 0, 1))
            alt = 22 * (1 - e) + 6  # sombra: más lejos mientras "cae"
            sx = int(pz["x"] + ox - pz["pad"] + alt * 0.6)
            sy = int(pz["y"] + oy - pz["pad"] + alt)
            negro = Image.new("RGBA", pz["sombra"].size, (0, 0, 0, 0))
            negro.putalpha(pz["sombra"])
            lienzo.alpha_composite(negro, (max(-9999, sx), sy)) if sx > -pz["sombra"].width else None
            lienzo.alpha_composite(pz["im"], (int(pz["x"] + ox + jx), int(pz["y"] + oy + jy))) \
                if pz["x"] + ox > -pz["im"].width else None
        ultimo = lienzo.convert("RGB").tobytes()
        proc.stdin.write(ultimo)
    proc.stdin.close()
    proc.wait()
    return sfx


def _alpha(lienzo, im, xy):
    """alpha_composite que tolera coordenadas negativas o fuera del cuadro."""
    x, y = xy
    caja = (max(0, -x), max(0, -y), min(im.width, W - x), min(im.height, H - y))
    if caja[2] <= caja[0] or caja[3] <= caja[1]:
        return
    lienzo.alpha_composite(im.crop(caja), (max(0, x), max(0, y)))


# alpha_composite de Pillow no acepta coordenadas negativas: lo envolvemos
_orig = Image.Image.alpha_composite


def _ac(self, im, dest=(0, 0), source=(0, 0)):
    if source == (0, 0) and len(dest) == 2 and (dest[0] < 0 or dest[1] < 0 or dest[0] + im.width > self.width
                                                 or dest[1] + im.height > self.height):
        return _alpha(self, im, (int(dest[0]), int(dest[1])))
    return _orig(self, im, (int(dest[0]), int(dest[1])), source)


Image.Image.alpha_composite = _ac


def clic_sfx(destino, seed):
    """Clic seco de proyector de diapositivas (dos golpecitos), hecho con ffmpeg."""
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"anoisesrc=d=0.03:c=white:a=0.8:s={seed}",
                    "-f", "lavfi", "-i", f"anoisesrc=d=0.04:c=brown:a=0.9:s={seed + 1}", "-filter_complex",
                    "[0]bandpass=f=2600:w=1800,afade=t=out:d=0.03[a];[1]lowpass=f=900,afade=t=out:d=0.04,adelay=55[b];"
                    "[a][b]amix=2:normalize=0,volume=1.2", "-ar", "44100", "-ac", "2", str(destino)], check=True)


def papel_sfx(destino, n, seed):
    """Sonido de papel pegado (ruido filtrado con envolvente rápida), hecho con ffmpeg."""
    dur = 0.22 + (seed % 3) * 0.03
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    f"anoisesrc=d={dur}:c=pink:a=0.9:s={seed}",
                    "-af", f"highpass=f=500,lowpass=f=6500,afade=t=in:d=0.004,"
                           f"afade=t=out:st=0.02:d={dur - 0.02}:curve=exp,volume=1.4",
                    "-ar", "44100", "-ac", "2", str(destino)], check=True)


# ───────────────────────── estilo "vox": explicativo moderno (papel crema, tags, resaltador, rebote) ─────────────────────────
CREMA = (242, 239, 232)
TINTA = (14, 26, 14)
VERDE_RES = (150, 214, 120)   # resaltador (ACENTO del canal, más vivo)
SOMBRA_VOX = (26, 46, 26)


def fondo_vox():
    base = Image.new("RGB", (W, H), CREMA)
    grano = Image.effect_noise((W, H), 22).convert("L").point(lambda v: 228 + v // 9)
    base = ImageChops.multiply(base, Image.merge("RGB", [grano] * 3))
    rnd = random.Random(5)
    d = ImageDraw.Draw(base)
    for _ in range(700):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        a, l = rnd.uniform(0, math.pi), rnd.uniform(5, 16)
        c = rnd.randint(214, 228)
        d.line([(x, y), (x + l * math.cos(a), y + l * math.sin(a))], fill=(c, c - 3, c - 9), width=1)
    v = Image.new("L", (W, H), 0)
    ImageDraw.Draw(v).ellipse([-W * 0.3, -H * 0.4, W * 1.3, H * 1.4], fill=255)
    v = v.filter(ImageFilter.GaussianBlur(200))
    return Image.composite(base, ImageChops.multiply(base, Image.new("RGB", (W, H), (225, 220, 208))), v)


def foto_vox(p):
    src = Image.open(RAIZ / p["archivo"]).convert("RGB")
    if "recorte" in p:
        src = src.crop(p["recorte"])
    cw, ch = p["celda"][2], p["celda"][3]
    src = ImageOps.fit(src, (cw, ch), Image.LANCZOS, centering=p.get("centro", (0.5, 0.5)))
    if p.get("bn"):
        src = ImageOps.colorize(ImageOps.grayscale(src), TINTA, CREMA)
    return src.convert("RGBA")


def etiqueta_vox(p):
    """Tag: caja de color con texto mono en mayúsculas."""
    f = fuente(p.get("tam", 30), peso=800)
    txt = p["texto"].upper()
    fondo_c = {"rojo": ROJO, "verde": VERDE_RES, "tinta": TINTA}.get(p.get("color", "tinta"))
    tinta = TINTA if p.get("color") == "verde" else CREMA
    asc, desc = f.getmetrics()
    w, h = int(f.getlength(txt)) + 40, asc + desc + 22
    im = Image.new("RGBA", (w, h), fondo_c + (255,))
    ImageDraw.Draw(im).text((20, 11), txt, font=f, fill=tinta + (255,))
    return im


OSCURO_FONDO = False  # True cuando el fondo es un clip/foto desenfocado (textos claros)


def fondos_vox(cfg, dur):
    """Cuadros de fondo por tramos: [{"t": seg_inicio, "archivo": clip o foto, "desde": seg}, ...]
    (desenfocado, lento, oscuro y teñido de verde, igual que las placas del canal). Sin "fondos": papel crema."""
    tramos = cfg.get("fondos")
    if not tramos:
        b = fondo_vox()
        for _ in range(int(dur * FPS)):
            yield b
        return
    sys.path.insert(0, str(RAIZ / "herramientas"))
    import graficos
    try:
        import armar
    except Exception:
        armar = None
    for i, tr in enumerate(tramos):
        fin = tramos[i + 1]["t"] if i + 1 < len(tramos) else dur
        arch = RAIZ / tr["archivo"]
        f = {"archivo": arch, "desde": tr.get("desde", 0)}
        if tr.get("limpio"):
            f["limpio"] = tr["limpio"]
        elif armar and arch.suffix.lower() == ".mp4":
            try:
                f["limpio"] = armar.filtro_limpio(arch)[0]
            except Exception:
                pass
        if arch.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):  # foto: desenfocada y teñida una sola vez
            im = ImageOps.fit(Image.open(arch).convert("RGB"), (W, H), Image.LANCZOS)
            im = im.filter(ImageFilter.GaussianBlur(tr.get("blur", 16)))
            im = Image.blend(im, Image.new("RGB", (W, H), (26, 46, 26)), tr.get("tinte", 0.5))
            im = ImageChops.multiply(im, _vineta())
            for _ in range(round((fin - tr["t"]) * FPS)):
                yield im
            continue
        yield from graficos._cuadros_fondo(f, W, H, fin - tr["t"])


def _vineta():
    v = Image.new("L", (W, H), 120)
    ImageDraw.Draw(v).ellipse([-W * 0.2, -H * 0.3, W * 1.2, H * 1.3], fill=255)
    return Image.merge("RGB", [v.filter(ImageFilter.GaussianBlur(180))] * 3)


def titulo_vox(p):
    """Título grande con resaltador que se pinta de izquierda a derecha: función prog -> RGBA."""
    f = fuente(p.get("tam", 110), mono=False, peso=760)
    lineas = p["texto"].split("\n")
    marcar = p.get("marcar", list(range(len(lineas))))
    asc, desc = f.getmetrics()
    lh = int((asc + desc) * 1.05)
    anchos = [f.getlength(l) for l in lineas]
    arriba = int(asc * 0.25)  # aire arriba: los acentos y las mayúsculas no se cortan
    w, h = int(max(anchos)) + 60, lh * len(lineas) + 20 + arriba

    def dibujar(prog):
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        for i, l in enumerate(lineas):
            if i in marcar:
                pr = max(0.0, min(1.0, prog * len(marcar) - marcar.index(i)))
                if pr > 0:
                    bb = f.getbbox(l)  # la barra cubre la letra entera (texto oscuro sobre fondo oscuro no se ve)
                    y0 = arriba + i * lh + bb[1] - 8
                    d.rectangle([0, y0, 18 + (anchos[i] + 24) * ease(pr), arriba + i * lh + bb[3] + 8],
                                fill=VERDE_RES + (255,))
            claro = OSCURO_FONDO and i not in marcar
            d.text((12, arriba + i * lh), l, font=f, fill=(CREMA if claro else TINTA) + (255,))
        return im
    return dibujar


def silueta_vox(p):
    cw, ch = p["celda"][2], p["celda"][3]
    im = Image.new("RGBA", (cw, ch), (214, 209, 196, 255))
    d = ImageDraw.Draw(im)
    cx = cw / 2
    r = cw * 0.17
    d.ellipse([cx - r, ch * 0.2, cx + r, ch * 0.2 + 2 * r], fill=(176, 170, 156, 255))
    d.rounded_rectangle([cx - cw * 0.36, ch * 0.2 + 2.2 * r, cx + cw * 0.36, ch * 1.15], radius=int(cw * 0.2),
                        fill=(176, 170, 156, 255))
    f = fuente(int(ch * 0.26), mono=False, peso=800)
    d.text((cx, ch * 0.2 + r), "?", font=f, fill=CREMA + (255,), anchor="mm")
    return im


def back(x):  # easeOutBack: pasa un poquito y vuelve
    x = max(0.0, min(1.0, x))
    c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def sonidos_vox(piezas):
    """[(t, clase)] de los efectos de un collage (whoosh por foto, pop por tag, marcador por título/círculo/flecha)."""
    clase = {"foto": "whoosh", "silueta": "whoosh", "etiqueta": "pop", "titulo": "marcador", "circulo": "marcador",
             "flecha": "marcador"}
    return [(float(p["en"]), clase[p["tipo"]]) for p in piezas if p["tipo"] in clase and not p.get("mudo")]


def render_vox(cfg, salida):
    texto, retardo, d_voz, dur = cfg["texto"], cfg["retardo"], cfg["d_voz"], cfg["duracion"]
    global OSCURO_FONDO
    OSCURO_FONDO = bool(cfg.get("fondos"))
    fondos = fondos_vox(cfg, dur)
    piezas, sonidos = [], []
    for k, p in enumerate(cfg["piezas"]):
        t0 = momento(texto, retardo, d_voz, p["en"])
        t1 = momento(texto, retardo, d_voz, p["sale"]) if "sale" in p else None
        tipo = p["tipo"]
        pz = {"t0": t0, "t1": t1, "sombra": False, "dyn": None, "im": None}
        if tipo in ("foto", "silueta"):
            pz["im"] = foto_vox(p) if tipo == "foto" else silueta_vox(p)
            pz["x"], pz["y"] = p["celda"][0], p["celda"][1]
            pz["sombra"] = True
            sonidos.append((t0, "whoosh"))
        elif tipo == "etiqueta":
            pz["im"] = etiqueta_vox(p).rotate(p.get("rot", 0), expand=True, resample=Image.BICUBIC)
            pz["x"], pz["y"] = p["x"], p["y"]
            sonidos.append((t0, "pop"))
        elif tipo == "titulo":
            pz["dyn"], pz["dur"] = titulo_vox(p), p.get("dibujo", 0.35)
            pz["x"], pz["y"] = p["x"], p["y"]
            sonidos.append((t0, "marcador"))
        elif tipo in ("circulo", "flecha"):
            pz["dyn"] = circulo(p) if tipo == "circulo" else flecha(p)
            pz["dur"] = p.get("dibujo", 0.5)
            pz["x"], pz["y"] = (p["x"], p["y"]) if tipo == "circulo" else (0, 0)
            pz["sin_rebote"] = True
            sonidos.append((t0, "marcador"))
        piezas.append(pz)
    n = int(dur * FPS)
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                             "-pix_fmt", "yuv420p", str(salida)], stdin=subprocess.PIPE)
    for fi in range(n):
        t = fi / FPS
        lienzo = next(fondos).convert("RGBA")
        for pz in piezas:
            if t < pz["t0"]:
                continue
            dx = dy = 0.0
            if not pz.get("sin_rebote") and pz["dyn"] is None:
                dy = 70 * (1 - back((t - pz["t0"]) / 0.3))
            if pz["t1"] is not None and t >= pz["t1"]:
                s_ = (t - pz["t1"]) / 0.22
                if s_ >= 1:
                    continue
                dx = -2300 * s_ ** 2
            if pz["dyn"] is not None:
                im = pz["dyn"]((t - pz["t0"]) / pz["dur"])
            else:
                im = pz["im"]
            x, y = int(pz["x"] + dx), int(pz["y"] + dy)
            if pz["sombra"]:
                sh = Image.new("RGBA", im.size, (0, 0, 0, 150) if OSCURO_FONDO else SOMBRA_VOX + (255,))
                lienzo.alpha_composite(sh, (x + 14, y + 14))
            lienzo.alpha_composite(im, (x, y))
        proc.stdin.write(lienzo.convert("RGB").tobytes())
    proc.stdin.close()
    proc.wait()
    return sonidos


def sfx_vox(destino, clase, seed):
    if clase == "whoosh":
        fil = (f"anoisesrc=d=0.32:c=pink:a=0.8:s={seed}", "highpass=f=300,lowpass=f=5000,"
               "afade=t=in:d=0.12:curve=qsin,afade=t=out:st=0.12:d=0.2:curve=exp,volume=0.9")
    elif clase == "pop":
        fil = ("sine=f=880:d=0.07", "afade=t=out:d=0.07:curve=exp,volume=0.5")
    else:  # marcador: chirrido corto de fibra
        fil = (f"anoisesrc=d=0.28:c=white:a=0.5:s={seed}", "bandpass=f=3800:w=2000,tremolo=f=28:d=0.6,"
               "afade=t=in:d=0.03,afade=t=out:st=0.18:d=0.1,volume=0.35")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", fil[0], "-af", fil[1],
                    "-ar", "44100", "-ac", "2", str(destino)], check=True)


def main():
    cfg_path = Path(sys.argv[1])
    cfg = json.loads(cfg_path.read_text())
    global SOBRIO
    SOBRIO = cfg.get("estilo") == "sobrio"
    tmp = cfg_path.parent / "tmp_collage"
    tmp.mkdir(exist_ok=True)
    video = tmp / "video.mp4"
    if cfg.get("estilo") == "vox":
        sonidos = render_vox(cfg, video)
        tiempos = [t for t, _ in sonidos]
    else:
        sonidos = None
        tiempos = render(cfg, video)
    # audio: voz + papel + música
    entradas, filtros = ["-i", str(video), "-i", str(RAIZ / cfg["voz"])], []
    filtros.append(f"[1:a]adelay={int(cfg['retardo'] * 1000)}:all=1,volume=1.0[voz]")
    mezcla = ["[voz]"]
    for i, t in enumerate(tiempos):
        f = tmp / f"papel_{i}.wav"
        if sonidos:
            sfx_vox(f, sonidos[i][1], 7 + i)
        else:
            clic_sfx(f, 7 + i) if SOBRIO else papel_sfx(f, i, 7 + i)
        entradas += ["-i", str(f)]
        filtros.append(f"[{i + 2}:a]adelay={int(t * 1000)}:all=1,volume=0.5[p{i}]")
        mezcla.append(f"[p{i}]")
    if cfg.get("musica"):
        m = cfg["musica"]
        entradas += ["-ss", str(m.get("desde_seg", 0)), "-i", str(RAIZ / m["archivo"])]
        k = len(tiempos) + 2
        filtros.append(f"[{k}:a]volume={m.get('volumen', 0.18)},afade=t=in:d=1,"
                       f"afade=t=out:st={cfg['duracion'] - 1.2}:d=1.2[mus]")
        mezcla.append("[mus]")
    filtros.append("".join(mezcla) + f"amix=inputs={len(mezcla)}:normalize=0,atrim=0:{cfg['duracion']}[a]")
    salida = RAIZ / cfg["salida"]
    salida.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex", ";".join(filtros),
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", str(salida)], check=True)
    print("listo:", salida)


if __name__ == "__main__":
    main()
