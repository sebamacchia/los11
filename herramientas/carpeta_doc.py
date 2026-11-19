"""CARPETA tranquila ("Vox", documental moderno de YouTube) — segunda parte de Argentina 86 (17/11).
Pedido del usuario: el estilo de la intro (recortes, papel, tiras, sellos) pero más calmo y documental: un papel
limpio de fondo (identidad/texturas/papel_vox.png, Higgsfield), pocas cosas a la vez que entran tranquilas
("aparece") y se van cuando cambia la idea, empuje lento de cámara, clips recortados a tijera (nunca a pantalla
completa), citas impresas en recortes de diario (diario_recorte.png, Higgsfield) con resaltador amarillo.

  herramientas/.venv/bin/python herramientas/carpeta_doc.py <escena|todas> [--capas] [--cap2]
  -> proyectos/argentina-1986/salida/graficos/p2_<escena>.mp4 (+ .sonidos.json, + _capas/)
Tiempos de palabra: whisper local sobre la voz de cada escena (tmp_guion_parte2/linea.json), voz en V segundos.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import carpeta as C  # noqa: E402
from carpeta import W, H, ROJO, TINTA, CREMA  # noqa: E402

RAIZ = C.RAIZ
P = RAIZ / "proyectos/argentina-1986"
M = P / "material"
G = P / "salida/graficos"
PERU = M / "fuentes/peru1985.mp4"
PERU_REC = (0, 62, 480, 352)            # sin la franja del logo de canal (igual que en la intro)
V = 0.4                                 # la voz arranca 0.4 s después del corte
AMARILLO = (247, 214, 72)
VOCES = ["89a504508e600702", "fc176f56edfbe23f", "79f0429ea8def61a", "e6c375709536a60c", "8d74472811c998b5",
         "75a7032076032fe5", "0053dc0847a0464c"]   # 6 y 7: rehechas 17/11 (precio del pase, enfermedad)


def plex(tam, peso=700):
    f = ImageFont.truetype(str(C.FUENTES / "plex-sans.ttf"), int(tam))
    try:
        f.set_variation_by_axes([peso])
    except Exception:
        pass
    return f


# ── papel y recorte por capítulo (18/11, pedido del usuario: que no canse; ver identidad/... y herramientas/marcos.py).
# Fuente, resaltador, etiquetas y sellos quedan iguales en todo: eso es LOS 11.
import marcos  # noqa: E402
C._recorte_tijera = getattr(C, "_recorte_tijera", C.recorte_cuadro)
TEMAS = {"crema": ("papel_vox.png", None, False), "cuadricula": ("papel_cuadricula.png", "cinta", False),
         "kraft": ("carton_kraft.png", "esquineros", False), "noche": ("cartulina_noche.png", "dentado", True),
         "diario": ("papel_diario.png", "laboratorio", False)}
TEMA_CAP = {"p2": "crema", "p3": "cuadricula", "p4": "kraft", "p5": "noche", "p6": "diario", "p7": "crema",
            "p8": "kraft", "p9": "noche", "p10": "cuadricula"}
TEMA = "crema"
TINTA_T = TINTA            # tinta sobre el papel (crema en la cartulina oscura)


def usar_tema(nombre):
    global TEMA, TINTA_T
    TEMA = nombre
    _, marco, oscuro = TEMAS[nombre]
    C.recorte_cuadro = marcos.MARCOS[marco] if marco else C._recorte_tijera
    TINTA_T = CREMA if oscuro else TINTA


def tema_de(n):
    return TEMA_CAP.get(str(n).split("_")[0] if isinstance(n, str) else "p2", "crema")


def fondo():
    return Image.open(C.TEX / TEMAS[TEMA][0]).convert("RGB").resize((W, H), Image.LANCZOS).convert("RGBA")


def foto(ruta, alto, caja=None, seed=3):
    im = Image.open(ruta).convert("RGB")
    if caja:
        im = im.crop(caja)
    im = im.resize((int(im.width * alto / im.height), int(alto)), Image.LANCZOS)
    a = np.asarray(im).astype("int16")                           # impreso: un poco cálido y con grano
    n = np.random.default_rng(seed).normal(0, 5, a.shape[:2])[..., None]
    a = np.clip(a * [0.98, 0.96, 0.9] + [5, 3, 0] + n, 0, 255).astype("uint8")
    out = C.recorte_cuadro(Image.fromarray(a), seed=seed)
    if any(k in str(ruta) for k in CUADRO_VIDEO):
        out.info["cuadro"] = (ruta, caja, seed)
    return out


def titulo(texto, tam=110, resaltar=True, color=None, peso=700):
    """Texto grande negro con resaltador amarillo detrás (una franja por renglón, a mano)."""
    color = color or (TINTA if resaltar else TINTA_T)
    f = plex(tam, peso)
    lineas = texto.split("\n")
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    anchos = [d0.textlength(l, font=f) for l in lineas]
    lh = int(tam * 1.12)
    im = Image.new("RGBA", (int(max(anchos) + tam * 0.6), lh * len(lineas) + int(tam * 0.3)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(len(texto))
    for i, (l, w) in enumerate(zip(lineas, anchos)):
        y = i * lh + tam * 0.18
        if resaltar:
            capa = Image.new("RGBA", im.size, (0, 0, 0, 0))
            dc = ImageDraw.Draw(capa)
            x0, x1 = tam * 0.12, tam * 0.3 + w + tam * 0.12
            y0, y1 = y + tam * 0.42, y + tam * 1.12
            dc.polygon([(x0, y0 + rng.uniform(-4, 4)), (x1, y0 + rng.uniform(-4, 4)),
                        (x1 + rng.uniform(-6, 6), y1), (x0 + rng.uniform(-6, 6), y1)], fill=AMARILLO + (215,))
            im.alpha_composite(capa)
        d.text((tam * 0.3, y), l, font=f, fill=color + (255,))
    return im


def diario(texto, ancho=560, tam=44, resaltar=False, arriba=None, seed=2):
    """Recorte de diario (textura de Higgsfield, fondo blanco quitado) con la cita impresa."""
    t = Image.open(C.TEX / "diario_recorte.png").convert("RGB")
    a = np.asarray(t).astype("int16")
    blanco = (a.min(axis=2) > 236)
    al = Image.fromarray(np.where(blanco, 0, 255).astype("uint8")).filter(C.ImageFilter.MedianFilter(5))
    t = t.convert("RGBA")
    t.putalpha(al)
    t = t.crop(al.getbbox())
    f = plex(tam, 600)
    fa = C.fuente(int(tam * 0.5), 600)
    lineas = texto.split("\n")
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    tw = max([d0.textlength(l, font=f) for l in lineas] + ([d0.textlength(arriba, font=fa)] if arriba else []))
    lh = int(tam * 1.2)
    alto_txt = lh * len(lineas) + (int(tam * 0.9) if arriba else 0)
    w = int(max(ancho, tw + tam * 1.6))
    h = int(alto_txt + tam * 1.8)
    t = t.resize((w, h), Image.LANCZOS)
    d = ImageDraw.Draw(t)
    y = tam * 0.85
    if arriba:
        d.text((tam * 0.8, y), arriba, font=fa, fill=(120, 40, 30, 255))
        y += tam * 0.9
    for l in lineas:
        if resaltar:
            lw = d.textlength(l, font=f)
            capa = Image.new("RGBA", t.size, (0, 0, 0, 0))
            ImageDraw.Draw(capa).rectangle((tam * 0.7, y + tam * 0.35, tam * 0.9 + lw, y + tam * 1.15),
                                           fill=AMARILLO + (190,))
            t.alpha_composite(capa)
        d.text((tam * 0.8, y), l, font=f, fill=(30, 26, 22, 255))
        y += lh
    return C.figurita(t, seed=seed)


def etiqueta(texto, tam=30, fondo=TINTA, seed=1):
    return C.tira(texto, tam=tam, fondo=fondo, seed=seed)


def cara(nombre, alto=200, seed=4):
    return foto(M / f"retratos/caras/{nombre}.png", alto, seed=seed)


def sin_blanco(ruta, alto, seed=5, umbral=236):
    """Ilustración de Higgsfield sobre blanco -> recorte sin fondo, con borde a tijera."""
    t = Image.open(ruta).convert("RGB")
    a = np.asarray(t).astype("int16")
    al = Image.fromarray(np.where(a.min(axis=2) > umbral, 0, 255).astype("uint8")).filter(C.ImageFilter.MedianFilter(5))
    t = t.convert("RGBA")
    t.putalpha(al)
    t = t.crop(al.getbbox())
    t = t.resize((int(t.width * alto / t.height), int(alto)), Image.LANCZOS)
    return C.figurita(t, seed=seed)


def circulo(w_, h_, grosor=9, seed=1):
    """Círculo de fibra roja hecho a mano (no cierra perfecto)."""
    im = Image.new("RGBA", (w_ + 40, h_ + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(seed)
    ang = np.linspace(-0.3, 2 * np.pi + 0.25, 140)
    r = 1 + 0.03 * np.sin(ang * 2 + rng.uniform(0, 6)) + np.linspace(0, 0.06, len(ang))
    pts = [(20 + w_ / 2 + w_ / 2 * rr * np.cos(a_), 20 + h_ / 2 + h_ / 2 * rr * np.sin(a_)) for a_, rr in zip(ang, r)]
    d.line(pts, fill=ROJO + (235,), width=grosor, joint="curve")
    return im


def flecha(largo=360, alto=120, grosor=10):
    """Flecha roja curva a mano, de izquierda a derecha (para "trazo")."""
    im = Image.new("RGBA", (largo + 40, alto + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    xs = np.linspace(0, 1, 60)
    pts = [(20 + largo * u, 30 + alto - alto * 4 * u * (1 - u)) for u in xs]
    d.line(pts, fill=ROJO + (240,), width=grosor, joint="curve")
    x1, y1 = pts[-1]
    d.line([(x1 - 46, y1 - 34), (x1, y1), (x1 - 52, y1 + 18)], fill=ROJO + (240,), width=grosor, joint="curve")
    return im


# ───── MODO TV (18/11, pedido del usuario): "que se vea la cancha más grande, que ocupe más (no pantalla completa
# pero casi) y los gráficos arriba"; el marcador "como lo pondría la tele arriba del video, no tan preponderante";
# sin círculos rojos ("muchas veces no está donde tiene que estar"). Se aplica al renderizar, en todas las piezas.
TV_ALTO, TV_ANCHO, TV_X, TV_Y = 900, 1720, W / 2, H / 2 + 6
CUADRO_VIDEO = ("congelados", "/assets/iv_", "collage/fifa_", "collage/fin_")


def marcador_tv(texto, sub, tam=34):
    """Marcador chico de TV: el resultado en una caja roja y el detalle en una franja oscura, sin papel."""
    f1, f2 = C.fuente(tam, 800), C.fuente(int(tam * 0.68), 600)
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    t1 = texto.replace("  ", " ")
    w1, w2 = d0.textlength(t1, font=f1), d0.textlength(sub, font=f2) if sub else 0
    h = int(tam * 1.65)
    a1, a2 = int(w1 + tam * 0.9), int(w2 + tam * 0.9) if sub else 0
    im = Image.new("RGBA", (a1 + a2 + 12, h + 12), (0, 0, 0, 0))
    sombra = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sombra).rectangle([5, 7, a1 + a2 + 5, h + 7], fill=(0, 0, 0, 120))
    im.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(4)))
    d = ImageDraw.Draw(im)
    if sub:
        d.rectangle([0, 0, a2, h], fill=TINTA + (238,))
        d.text((tam * 0.45, h / 2), sub, font=f2, fill=CREMA, anchor="lm")
    d.rectangle([a2, 0, a2 + a1, h], fill=ROJO + (250,))
    d.text((a2 + a1 / 2, h / 2), t1, font=f1, fill=(255, 255, 255), anchor="mm")
    return im


def _caja(e):
    """(cx, cy, ancho, alto) en pantalla de un video o una imagen."""
    if e.get("video"):
        rec, an = e["video"][3], e["video"][4]
        return e["x"], e["y"], an, an * (rec[3] - rec[1]) / (rec[2] - rec[0])
    return e["x"], e["y"], e["img"].width, e["img"].height


def _encima(a, b):
    return a["t"] < b.get("hasta", 1e9) and a.get("hasta", 1e9) > b["t"]


def modo_tv(E, dur):
    E = [e for e in E if not str(e.get("nombre") or "").startswith("circulo")]
    cand = [e for e in E if not (e.get("chico") or e.get("mosaico")) and (e.get("video") or (
        e.get("img") is not None and e["img"].info.get("cuadro") and e["img"].height >= 380))]
    objs = []
    for e in cand:
        otros = [o for o in cand if o is not e and _encima(e, o)
                 and min(e.get("hasta", dur), o.get("hasta", dur)) - max(e["t"], o["t"]) > 0.4]
        if otros and not all(abs(o["x"] - e["x"]) < 80 and abs(o["y"] - e["y"]) < 80 for o in otros):
            continue                                   # varios cuadros a la vez en lugares distintos (grilla): se dejan
        objs.append(e)
    hijos = set()
    for o in objs:
        ox, oy, ow, oh = _caja(o)
        asp = ow / oh
        nh = TV_ALTO
        nw = nh * asp
        if nw > TV_ANCHO:
            nw, nh = TV_ANCHO, TV_ANCHO / asp
        k = nw / ow
        if o.get("video"):
            src, desde, vel, rec, an = o["video"]
            o["video"] = (src, desde, vel, rec, int(nw) // 2 * 2)
        else:
            ruta, caja, seed = o["img"].info["cuadro"]
            o["img"] = foto(ruta, nh, caja=caja, seed=seed)
        o["x"], o["y"] = TV_X, TV_Y
        o["rot"] = max(-0.5, min(0.5, o.get("rot", 0.0) * 0.3))
        o["_tv"] = (TV_X - nw / 2, TV_Y - nh / 2, nw, nh)
        for c in E:
            if c is o or c in objs or id(c) in hijos or c.get("video") or c.get("img") is None or not _encima(c, o):
                continue
            if c["img"].info.get("marcador"):
                continue
            if abs(c["x"] - ox) < ow / 2 and abs(c["y"] - oy) < oh / 2:      # estaba sobre el cuadro: se muda con él
                hijos.add(id(c))
                c["x"], c["y"] = TV_X + (c["x"] - ox) * k, TV_Y + (c["y"] - oy) * k
                if c["img"].info.get("dibujo"):
                    c["img"] = c["img"].resize((int(c["img"].width * k), int(c["img"].height * k)), Image.LANCZOS)
            elif c["img"].width > 520 or c["img"].height > 420:             # al costado y grande: más chico, arriba
                f = min(520 / c["img"].width, 420 / c["img"].height)
                info = dict(c["img"].info)
                c["img"] = c["img"].resize((int(c["img"].width * f), int(c["img"].height * f)), Image.LANCZOS)
                c["img"].info.update(info)
                hijos.add(id(c))
    # marcadores encima de un video: marcador de TV arriba a la izquierda del cuadro
    bugs = []
    for c in E:
        if c.get("img") is None or not c["img"].info.get("marcador"):
            continue
        o = next((o for o in objs if _encima(c, o)), None)
        if o is None:
            continue
        x0, y0, nw, nh = o["_tv"]
        c["img"] = marcador_tv(*c["img"].info["marcador"])
        c["x"], c["y"] = x0 + 40 + c["img"].width / 2, y0 + 34 + c["img"].height / 2
        c["rot"], c["entrada"], c["dura"] = 0.0, "aparece", 0.25
        c["hasta"] = min(c.get("hasta", 1e9), o.get("hasta", dur))     # no queda flotando cuando termina el video
        bugs.append(c)
    bugs.sort(key=lambda c: c["t"])
    for a_, b_ in zip(bugs, bugs[1:]):
        if abs(a_["x"] - b_["x"]) < 400 and abs(a_["y"] - b_["y"]) < 60:
            a_["hasta"] = min(a_.get("hasta", 1e9), b_["t"])
    for b_ in bugs:                                            # lo que choca con el marcador baja un poco
        bx0, by0 = b_["x"] - b_["img"].width / 2, b_["y"] - b_["img"].height / 2
        bx1, by1 = bx0 + b_["img"].width, by0 + b_["img"].height
        for c in E:
            if c is b_ or c in bugs or c.get("img") is None or c.get("video") or c in objs or not _encima(c, b_):
                continue
            cw, ch = c["img"].width, c["img"].height
            if c["x"] - cw / 2 < bx1 and c["x"] + cw / 2 > bx0 and c["y"] - ch / 2 < by1 and c["y"] + ch / 2 > by0:
                c["y"] = by1 + ch / 2 + 12
    # entre dos cuadros grandes seguidos no queda un destello de papel: el anterior sigue hasta que entra el otro
    pos = {id(e): i for i, e in enumerate(E)}
    seq = sorted(objs, key=lambda e: e["t"])
    for o1, o2 in zip(seq, seq[1:]):
        fin = o1.get("hasta", dur)
        if pos[id(o2)] > pos[id(o1)] and -0.1 <= o2["t"] - fin <= 0.6:
            o1["hasta"] = max(fin, o2["t"] + o2.get("dura", 0.35) + 0.05)
            if o1.get("video"):
                o1["vdur"] = o1["hasta"] - o1["t"] + 0.3
    # los gráficos que se ven mientras corre un video en modo TV van ENCIMA (aunque se hayan puesto antes)
    arriba = []
    for c in E:
        if c.get("img") is None or c in objs or c.get("video"):
            continue
        tapa = [o for o in objs if pos[id(o)] > pos[id(c)] and _encima(c, o)]
        if not tapa:
            continue
        if all(c["t"] < o["t"] - 0.3 for o in tapa):     # venía de antes: se va cuando entra el video
            c["hasta"] = min(c.get("hasta", 1e9), min(o["t"] for o in tapa) + 0.35)
        else:
            arriba.append(c)
    if arriba:
        ids = {id(c) for c in arriba}
        E = [e for e in E if id(e) not in ids] + arriba
    for c in E:                                                # nada cortado contra el borde
        if c.get("img") is not None and not c.get("mov") and c["img"].width < W - 40:
            c["x"] = min(max(c["x"], c["img"].width / 2 + 20), W - c["img"].width / 2 - 20)
            c["y"] = min(max(c["y"], c["img"].height / 2 + 16), H - c["img"].height / 2 - 16)
    return E


MOSAICO = {1: [(TV_X, TV_Y, 1.0)],
           2: [(490, 545, 0.52), (1430, 545, 0.52)],
           3: [(500, 300, 0.5), (1420, 300, 0.5), (960, 790, 0.5)]}


def goles_juntos(s, goles, hasta):
    """Varios goles en la misma pantalla (18/11, pedido del usuario): el primero ocupa todo; cuando llega el
    segundo, el primero se achica a un costado y sigue corriendo, y así con el tercero. goles: dicts con desde, t,
    src, rec, vel, nombre, texto, sub (marcador de TV de ese gol, aparece en t_marca)."""
    n = len(goles)
    for i, g in enumerate(goles):
        rc = g["rec"]
        asp = (rc[2] - rc[0]) / (rc[3] - rc[1])
        an = min(TV_ANCHO, TV_ALTO * asp)
        al = an / asp
        x, y, e0 = MOSAICO[i + 1][i]
        movs, bmovs = [], []
        bug = marcador_tv(g["texto"], g.get("sub", ""), tam=34)
        off = lambda e: (-an * e / 2 + 26 + bug.width / 2, -al * e / 2 + 22 + bug.height / 2)
        px, py, pe = x, y, e0
        bx, by = px + off(pe)[0], py + off(pe)[1]
        bx0, by0 = bx, by
        for j in range(i + 1, n):
            tj = goles[j]["t"]
            nx, ny, ne = MOSAICO[j + 1][i]
            movs.append((tj, tj + 0.5, nx - px, ny - py, "s", 0.0, ne / pe))
            nbx, nby = nx + off(ne)[0], ny + off(ne)[1]
            bmovs.append((tj, tj + 0.5, nbx - bx, nby - by, "s"))
            px, py, pe, bx, by = nx, ny, ne, nbx, nby
        s.E.append(dict(img=None, x=x, y=y, t=g["t"], hasta=hasta, rot=0.0, nombre=g["nombre"], entrada="aparece",
                        dura=0.3, sonido=False, video=(g["src"], g["desde"], g["vel"], rc, int(an) // 2 * 2),
                        vdur=hasta - g["t"] + 0.3, esc=e0, mov=movs, mosaico=True))
        s.E.append(dict(img=bug, x=bx0, y=by0, t=g.get("t_marca", g["t"]), hasta=hasta, rot=0.0,
                        nombre=g["nombre"] + "_marcador", entrada="aparece", dura=0.25,
                        sonido=g.get("sonido", SELLO), mov=bmovs, mosaico=True))


class Escena:
    def __init__(self, n, dur):
        self.n, self.dur, self.E = n, dur, []
        usar_tema(tema_de(n))

    def pon(self, img, x, y, t, rot=0.0, nombre=None, entrada="aparece", dura=0.6, sonido=False, **kw):
        if img is not None and not kw.get("mov") and img.width < W - 40:   # 18/11: nada cortado contra el borde
            x = min(max(x, img.width / 2 + 20), W - img.width / 2 - 20)
            y = min(max(y, img.height / 2 + 16), H - img.height / 2 - 16)
        self.E.append(dict(img=img, x=x, y=y, t=t, rot=rot, nombre=nombre, entrada=entrada, dura=dura,
                           sonido=sonido, **kw))

    def clip(self, desde, t, hasta, ancho=1100, x=W / 2, y=H / 2, vel=0.6, rot=0.0, nombre="clip", src=PERU,
             rec=PERU_REC, entrada="aparece", dura=0.35, **kw):
        if t < 0:                                   # arranca antes del corte: se adelanta el video
            desde, t = desde - t * vel, 0.0
        self.E.append(dict(img=None, x=x, y=y, t=t, hasta=hasta, rot=rot, nombre=nombre, entrada=entrada,
                           dura=dura, sonido=False, video=(src, desde, vel, rec, ancho),
                           vdur=hasta - t + 0.3, **kw))

    def render(self, capas=False, solo=None, camara=None):
        salida = G / (f"{self.n}.mp4" if isinstance(self.n, str) else f"p2_{self.n}.mp4")
        self.E = modo_tv(self.E, self.dur) if getattr(self, "tv", True) else self.E
        if camara and any(e.get("_tv") or e.get("mosaico") for e in self.E):   # el zoom no corta el marcador de TV
            camara = [(t, min(z, 1.05), W / 2 + (cx - W / 2) * 0.3, H / 2 + (cy - H / 2) * 0.3) for t, z, cx, cy in camara]
        C.pila(salida, self.E, self.dur, base=fondo(), capas=capas, solo=solo, camara=camara)
        if not solo:
            json.dump(C.sonidos_de(self.E), open(salida.with_suffix(".sonidos.json"), "w"), indent=1)
            # para el Vibe Editor (pista de animación) sin tener que generar las capas ProRes
            json.dump([{"nombre": e.get("nombre") or "pila", "inicio": round(e["t"], 3),
                        "fin": round(min(e.get("hasta") or self.dur, self.dur), 3)} for e in self.E],
                      open(salida.with_suffix(".elementos.json"), "w"), ensure_ascii=False, indent=1)
        return salida


def w(t):
    return t + V


SELLO = {"archivo": "sello_thump", "vol": 0.55}
PAPEL = {"archivo": "carta", "vol": 0.45}


def e1():
    """Para entender México, hay que volver un año atrás. 30 de junio de 1985. Cancha de River. Última fecha de la
    eliminatoria. Argentina contra Perú."""
    s = Escena(1, 12.4)
    # "Para entender México": el afiche oficial del Mundial (no el texto "Un año atrás")
    s.pon(foto(M / "intro/afiches/1986.png", 720, seed=8), W / 2, 540, w(0.2), rot=-2, nombre="afiche_86", sonido=PAPEL,
          hasta=w(3.5))
    s.pon(etiqueta("30 DE JUNIO DE 1985", 40), 520, 470, w(3.6), rot=-1.5, nombre="fecha", entrada="golpe",
          dura=0.1, sonido=PAPEL)
    s.pon(foto(M / "tribuna_peru1985.jpg", 180, caja=(0, 0, 980, 205)), 1420, 230, w(5.9), rot=1.2,
          nombre="tribuna_river")
    s.pon(etiqueta("MONUMENTAL · RIVER PLATE", 26), 1420, 350, w(6.4), rot=1, nombre="lugar")
    s.pon(diario("ÚLTIMA FECHA\nELIMINATORIAS", 520, 46, arriba="MÉXICO 86 · GRUPO 1"), 560, 720, w(7.9), rot=-2,
          nombre="ultima_fecha", sonido=PAPEL)
    s.clip(8.0, w(9.4), 12.4, ancho=760, x=1330, y=760, rot=1.5, nombre="clip_salida")
    s.pon(etiqueta("ARGENTINA  vs  PERÚ", 34, fondo=ROJO), 1330, 1000, w(9.6), rot=-1, nombre="partido",
          entrada="golpe", dura=0.1, sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (12.4, 1.06, W / 2, H / 2)]


def marcador(texto, sub, seed=5):
    im = diario(texto, 380, 120, arriba=sub, seed=seed)
    im.info["marcador"] = (texto, sub)
    return im


def e2():
    """Con un empate, Argentina iba al Mundial. Y arrancó ganando. Pasculli, a los 12. Pero Perú lo dio vuelta antes
    del entretiempo. Velázquez y Barbadillo, 2 a 1. Y a 10 minutos del final, el país entero estaba a 10 minutos de
    quedarse afuera."""
    s = Escena(2, 18.6)
    s.clip(12.4, w(0.3), w(2.6), ancho=1000, x=W / 2, y=540, rot=-1, nombre="clip_arranque")
    # los tres goles: el clip recortado a la izquierda, el marcador en un recorte de diario a la derecha
    # los tres goles en la misma pantalla: cada uno sigue corriendo mientras entra el siguiente
    goles_juntos(s, [dict(desde=19.5 - (w(4.54) - w(2.6)) * 0.6, t=w(2.6), src=PERU, rec=PERU_REC, vel=0.6,
                          nombre="gol_pasculli", texto="ARG 1-0 PER", sub="PASCULLI 12'", t_marca=w(4.6)),
                     dict(desde=65.5 - (w(9.18) - w(6.3)) * 0.6, t=w(6.3), src=PERU, rec=PERU_REC, vel=0.6,
                          nombre="gol_velasquez", texto="ARG 1-1 PER", sub="VELÁSQUEZ 23'", t_marca=w(9.2)),
                     dict(desde=136.3 - (w(11.0) - w(9.5)) * 0.6, t=w(9.5), src=PERU, rec=PERU_REC, vel=0.6,
                          nombre="gol_barbadillo", texto="ARG 1-2 PER", sub="BARBADILLO 39'", t_marca=w(11.0))],
                 hasta=w(12.7))
    s.pon(marcador("1 - 2", "ARG · PER", seed=7), 1580, 420, w(12.7), nombre="m12", sonido=False)
    s.clip(190.0, w(12.7), 18.6, x=760, y=560, rot=1.5, nombre="minuto80", ancho=1000)
    s.pon(etiqueta("MINUTO 80", 34, fondo=ROJO), 560, 230, w(13.0), rot=-2, nombre="minuto80_tira",
          entrada="golpe", dura=0.1, sonido=PAPEL)
    s.pon(foto(M / "peru85_enmudecidos.jpg", 380, seed=13), 1560, 820, w(14.2), rot=2, nombre="enmudecidos",
          sonido=PAPEL)
    return s, [(0, 1.0, W / 2, H / 2), (w(12.7), 1.0, W / 2, H / 2), (18.6, 1.07, 1100, 640)]


def e3():
    """Passarella le pega, la pelota da en el palo y en el rebote aparece Ricardo Gareca. Dos a dos. Argentina al
    Mundial. Por la ventana."""
    s = Escena(3, 10.6)
    s.clip(215.5 - (w(5.88) - w(0.0)) * 0.6, 0.0, w(6.5), x=760, y=540, rot=1, nombre="gol_gareca", ancho=1150)
    s.pon(etiqueta("PASSARELLA · PALO", 30), 520, 150, w(2.3), rot=-2, nombre="palo", hasta=w(6.5))
    s.pon(foto(M / "eg_gareca_peru.jpg", 380, seed=9), 1560, 360, w(4.1), rot=2, nombre="gareca")
    s.pon(etiqueta("RICARDO GARECA · 81'", 30), 1560, 580, w(4.5), rot=-1, nombre="gareca_nombre")
    s.pon(marcador("2 - 2", "ARG · PER", seed=10), 1560, 820, w(5.9), rot=-2, nombre="m22", entrada="golpe",
          dura=0.1, sonido=SELLO)
    s.pon(foto(M / "eg_passarella_peru.jpg", 620, seed=11), 720, 520, w(6.6), rot=-2, nombre="tapa_vamos_mexico",
          sonido=PAPEL)
    s.pon(C.sello("POR LA VENTANA", tam=90, rot=-5, seed=12), 720, 760, w(8.5), nombre="ventana", entrada="golpe",
          dura=0.08, sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (10.6, 1.05, W / 2, H / 2)]


def e4():
    """Bilardo y todos los que lo criticaban; cada crítico entra con su cita y se va cuando llega el siguiente."""
    s = Escena(4, 26.7)
    s.pon(foto(M / "eg_bilardo86.jpg", 760, caja=(4, 0, 546, 729), seed=11), 430, 560, w(0.9), rot=-1.2,
          nombre="bilardo")
    s.pon(etiqueta("CARLOS BILARDO · DT", 30), 430, 980, w(1.5), rot=1, nombre="bilardo_nombre")
    crit = [  # (foto, caja, nombre, cita, fuente, desde, hasta)
        (M / "menotti_fumando.jpg", (0, 22, 286, 407), "MENOTTI · CAMPEÓN 1978", "«Cobarde y\nenano mental»",
         None, 4.8, 9.7),
        (None, None, None, "«Argentina está\ndiez años atrasada»", "L'ÉQUIPE · PARÍS · 1/4/1986", 9.8, 14.1),
        (M / "retratos/caras/giusti.png", (42, 0, 287, 330), "RICARDO GIUSTI", "Silbado en su club\npor jugar en la selección",
         None, 14.2, 17.9),
        (M / "alfonsin.jpg", (4, 0, 800, 1072), "RAÚL ALFONSÍN · PRESIDENTE", "«¿Qué estás esperando\npara echarlo?»",
         None, 18.0, 30.0),
    ]
    for k, (fo, caja, nom, cita, fuente, a, b) in enumerate(crit):
        if fo:
            s.pon(foto(fo, 440, caja=caja, seed=20 + k), 1060, 600, w(a), rot=(-1) ** k * 1.5, nombre=f"critico{k}",
                  hasta=w(b))
            s.pon(etiqueta(nom, 24), 1060, 850, w(a + 0.3), rot=(-1) ** (k + 1), nombre=f"critico{k}_nombre",
                  hasta=w(b))
        s.pon(diario(cita, 560, 48, resaltar=True, arriba=fuente, seed=30 + k), 1500 if fo else 1300, 600,
              w(a + 0.9), rot=(-1) ** (k + 1) * 1.5, nombre=f"cita{k}", hasta=w(b), sonido=PAPEL)
    s.pon(C.sello("FALTABAN 50 DÍAS", tam=90, rot=-4, seed=14), 1350, 960, w(23.8), nombre="cincuenta_dias",
          entrada="golpe", dura=0.08, sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (26.7, 1.05, 900, 560)]


def e5():
    """Maradona lo bancó: si lo tocan a Bilardo, nos vamos todos. Pero Bilardo tenía una idea fija... un solo hombre.
    Y a ese hombre le dio la cinta de capitán. Diego Armando Maradona. 25 años."""
    s = Escena(5, 17.2)
    s.pon(foto(M / "eg_besa_camiseta.jpg", 620, caja=(60, 48, 598, 513), seed=15), 620, 540, w(0.0), rot=-1.5,
          nombre="banca", hasta=w(4.5))
    s.pon(diario("«Si lo tocan a Bilardo,\nnos vamos todos»", 640, 50, resaltar=True, arriba="MARADONA"), 1400, 540,
          w(1.4), rot=2, nombre="cita_banca", hasta=w(4.5), sonido=PAPEL)
    equipo = ["pumpido", "cuciuffo", "brown", "ruggeri", "giusti", "batista", "enrique", "olarticoechea",
              "burruchaga", "valdano"]
    for k, n in enumerate(equipo):
        ang = np.pi * (0.1 + 0.8 * k / 9)
        x, y = W / 2 - 760 * np.cos(ang), 560 + 340 * np.sin(ang) - 120
        s.pon(cara(n, 200, seed=40 + k), x, y, w(6.5 + 0.22 * k), rot=(k % 3 - 1) * 2, nombre=f"j_{n}",
              hasta=w(10.2), dura=0.4)
    s.pon(foto(M / "diego_pelota_azteca.jpg", 360, seed=50), W / 2, 470, w(9.0), nombre="diego_centro", hasta=w(10.2))
    s.pon(foto(M / "eg_besa_camiseta.jpg", 760, caja=(60, 48, 598, 513), seed=16), 700, 540, w(10.3), rot=1,
          nombre="capitan")
    cinta = C.piezas("cinta")[0]
    cinta = cinta.resize((260, int(cinta.height * 260 / cinta.width)), Image.LANCZOS)
    s.pon(C.tira("CAPITÁN", tam=56, fondo=ROJO, seed=3), 1420, 420, w(11.3), rot=-3, nombre="capitan_tira",
          entrada="golpe", dura=0.1, sonido=SELLO)
    s.pon(titulo("Diego Armando\nMaradona", 92), 1420, 640, w(13.2), nombre="diego_nombre")
    s.pon(etiqueta("25 AÑOS", 40), 1420, 840, w(14.9), rot=2, nombre="edad", entrada="golpe", dura=0.1,
          sonido=PAPEL)
    return s, [(0, 1.0, W / 2, H / 2), (w(10.2), 1.0, W / 2, H / 2), (17.2, 1.06, 1000, 560)]


LLUVIA = {"archivo": str(RAIZ / ".cache/elevenlabs/sfx_01e38e154dda870e.mp3"), "vol": 0.5, "dur": 3.0}
CONGELA = {"archivo": str(RAIZ / ".cache/elevenlabs/sfx_94456f0506b93f2f.mp3"), "vol": 0.6, "dur": 1.2}
F82 = M / "fuentes/gentile1982_b.mp4"
F82_REC = (0, 130, 1920, 1080)                  # sin el "Faltan 26 días" del video
FBR = M / "fuentes/expulsion1982.mp4"
FBR_REC = (260, 0, 1640, 1000)                  # sin las barras ni la marca de agua
CONG = M / "congelados"


def e6():
    """La gran estrella del mundo, Nápoles; el pase Barcelona -> Nápoles por US$ 7.500.000 (lluvia de dólares);
    España 82: las patadas de Gentile congeladas y agrandadas, la patada a Batista y la expulsión."""
    s = Escena(6, 24.6)
    fin_a = w(5.4)
    s.pon(foto(M / "maradona_napoli_fotografos.jpg", 560, seed=17), 640, 470, w(0.2), rot=-1.5, nombre="napoli",
          hasta=fin_a)
    s.pon(foto(M / "napoli_presentacion.jpg", 420, seed=18), 1430, 330, w(0.9), rot=2, nombre="san_paolo",
          sonido=PAPEL, hasta=fin_a)
    s.pon(etiqueta("SAN PAOLO · 70.000 PARA VERLO LLEGAR", 26), 1430, 580, w(1.4), rot=-1, nombre="san_paolo_tira",
          hasta=fin_a)
    s.pon(etiqueta("NÁPOLES · ITALIA", 30), 640, 800, w(3.2), rot=1, nombre="napoles", hasta=fin_a)
    # el pase: Barcelona -> Nápoles, el precio y la lluvia de dólares
    fin_b = w(13.5)
    s.pon(etiqueta("1984", 60), W / 2, 190, w(5.6), rot=-2, nombre="anio_pase", entrada="golpe", dura=0.1,
          sonido=PAPEL, hasta=fin_b)
    s.pon(foto(M / "maradona_companeros_napoli.jpg", 560, caja=(640, 0, 1140, 761), seed=60), 1460, 470, w(6.5),
          rot=2, nombre="pase_napoli", hasta=fin_b)
    s.pon(etiqueta("NÁPOLES", 34, fondo=ROJO), 1480, 760, w(6.7), rot=-1.5, nombre="pase_napoli_tira", hasta=fin_b)
    s.pon(foto(M / "maradona_barcelona.jpg", 560, caja=(130, 0, 780, 663), seed=61), 440, 460, w(8.1), rot=-2,
          nombre="pase_barcelona", hasta=fin_b)
    s.pon(etiqueta("BARCELONA", 34), 440, 760, w(8.3), rot=1.5, nombre="pase_barcelona_tira", hasta=fin_b)
    # (18/11, pedido del usuario: sin las flechas rojas a mano)
    billete = sin_blanco(M / "collage/billete_100.png", 110, seed=62)
    rng = np.random.default_rng(7)
    for k in range(34):
        t0 = w(9.0) + k * 0.11 + rng.uniform(0, 0.08)
        x0 = rng.uniform(80, W - 80)
        caida = rng.uniform(2.2, 3.2)
        s.pon(billete.rotate(rng.uniform(-40, 40), expand=True, resample=Image.BICUBIC), x0, -120, t0,
              rot=rng.uniform(-20, 20), nombre=f"billete{k:02d}", entrada="corte", dura=0.1,
              mov=[(t0, t0 + caida, rng.uniform(-160, 160), 1400, "lineal", rng.uniform(-90, 90))],
              hasta=min(t0 + caida, fin_b), sonido=LLUVIA if k == 0 else False)
    s.pon(titulo("US$ 7.500.000", 120), W / 2, 905, w(8.8), nombre="precio", entrada="golpe", dura=0.1,
          sonido=SELLO, hasta=fin_b)
    s.pon(C.sello("RÉCORD MUNDIAL", tam=80, rot=-5, seed=63), W / 2, 680, w(11.3), nombre="record",
          entrada="golpe", dura=0.08, sonido=SELLO, hasta=fin_b)
    s.pon(foto(M / "intro/afiches/1982.jpg", 760, seed=67), W / 2, 540, w(13.7), rot=-1.5, nombre="afiche_82",
          sonido=PAPEL, hasta=w(16.5))
    # España 82: el clip de Gentile, congelado y agrandado cuando Diego cae
    s.pon(etiqueta("ESPAÑA 82", 44, fondo=ROJO), 420, 140, w(16.6), rot=-2, nombre="espana", hasta=w(20.2))
    s.clip(48.6, w(16.7), w(18.3), ancho=1000, x=820, y=600, rot=-1, nombre="clip_gentile", src=F82, rec=F82_REC)
    s.pon(foto(CONG / "gentile_patada1.png", 640, seed=64), 820, 600, w(18.25), rot=-1.5, nombre="congelado1",
          entrada="golpe", dura=0.12, sonido=CONGELA, hasta=w(20.2))
    s.pon(circulo(430, 400), 690, 560, w(18.5), nombre="circulo_diego", entrada="trazo", dura=0.35, hasta=w(20.2))
    s.pon(etiqueta("CLAUDIO GENTILE · ITALIA", 28), 820, 960, w(18.6), rot=1, nombre="gentile", hasta=w(20.2))
    s.pon(foto(CONG / "gentile_patada2.png", 300, seed=65), 1480, 420, w(19.0), rot=3, nombre="congelado2",
          sonido=PAPEL, hasta=w(20.2))
    # Brasil: la patada a Batista y la roja
    s.clip(40.9, w(20.3), w(21.95), ancho=920, x=760, y=560, rot=1, nombre="clip_batista", src=FBR, rec=FBR_REC)
    s.pon(foto(CONG / "expulsion_batista.png", 680, seed=66), 700, 560, w(21.9), rot=1.5, nombre="congelado3",
          entrada="golpe", dura=0.12, sonido=CONGELA)
    s.pon(etiqueta("vs BRASIL · PATADA A BATISTA", 30), 1500, 230, w(22.1), rot=-1, nombre="batista")
    s.pon(C.tarjeta_roja(240), 1560, 560, w(22.3), rot=12, nombre="roja", entrada="golpe", dura=0.1, sonido=SELLO)
    s.pon(C.sello("EXPULSADO", tam=100, rot=-6, seed=15), 1500, 850, w(22.5), nombre="expulsado", entrada="golpe",
          dura=0.08, sonido=False)
    return s, [(0, 1.0, W / 2, H / 2), (w(13.5), 1.04, W / 2, H / 2), (w(16.6), 1.0, W / 2, H / 2),
               (w(18.2), 1.0, W / 2, H / 2), (w(20.1), 1.1, 720, 560), (w(20.2), 1.0, W / 2, H / 2),
               (24.6, 1.06, 1100, 560)]


def e7():
    """Passarella se enfermó en México: infección intestinal, la venganza de Moctezuma, diarrea y deshidratación;
    no jugó ni un minuto. El equipo era de Diego. ¿Para bien o para mal?"""
    s = Escena(7, 23.0)
    fin_a = w(8.7)
    s.pon(foto(M / "diego_passarella_sombreros.jpg", 900, caja=(0, 120, 1920, 1800), seed=19), 700, 540, w(0.0),
          rot=-1, nombre="sombreros", hasta=fin_a)
    s.pon(etiqueta("DANIEL PASSARELLA · CAPITÁN EN 1978", 28), 1300, 860, w(5.9), rot=-1, nombre="passarella",
          hasta=fin_a)
    s.pon(C.sello("ENFERMO", tam=100, rot=-7, seed=16), 1430, 250, w(7.1), nombre="enfermo", entrada="golpe",
          dura=0.08, sonido=SELLO, hasta=fin_a)
    # qué tuvo: el intestino dibujado, el parte médico, Moctezuma
    fin_b = w(15.2)
    s.pon(sin_blanco(M / "collage/intestinos.png", 800, seed=70), 560, 560, w(8.9), rot=-1, nombre="intestinos",
          sonido=PAPEL, hasta=fin_b)
    s.pon(circulo(520, 420, seed=3), 560, 680, w(9.5), nombre="circulo_intestino", entrada="trazo", dura=0.4,
          hasta=fin_b)
    s.pon(diario("Enterocolitis", 520, 54, resaltar=True, arriba="PARTE MÉDICO · PASSARELLA · MAYO 1986", seed=71),
          1400, 190, w(9.2), rot=2, nombre="parte_medico", sonido=PAPEL, hasta=fin_b)
    s.pon(sin_blanco(M / "collage/moctezuma.png", 440, seed=72), 1400, 590, w(10.7), rot=-2, nombre="moctezuma",
          hasta=fin_b)
    s.pon(etiqueta("«LA VENGANZA DE MOCTEZUMA»", 30, fondo=ROJO), 1400, 860, w(11.2), rot=1.5,
          nombre="venganza", entrada="golpe", dura=0.1, sonido=PAPEL, hasta=fin_b)
    s.pon(C.sello("DIARREA", tam=64, rot=-8, seed=73), 330, 250, w(13.1), nombre="diarrea", entrada="golpe",
          dura=0.08, sonido=SELLO, hasta=fin_b)
    s.pon(C.sello("DESHIDRATACIÓN", tam=60, rot=4, seed=74), 640, 960, w(13.5), nombre="deshidratacion",
          entrada="golpe", dura=0.08, sonido=SELLO, hasta=fin_b)
    # ni un minuto
    fin_c = w(17.3)
    s.pon(foto(M / "diego_passarella_sombreros.jpg", 680, caja=(980, 200, 1900, 1800), seed=75), 640, 540, w(15.3), rot=-1.5, nombre="passarella_foto",
          hasta=fin_c)
    s.pon(titulo("0 minutos", 140), 1420, 440, w(15.6), nombre="cero", entrada="golpe", dura=0.1, sonido=SELLO,
          hasta=fin_c)
    s.pon(etiqueta("MÉXICO 86 · NO JUGÓ NI UN MINUTO", 30, fondo=ROJO), 1420, 640, w(16.0), rot=2,
          nombre="ni_un_minuto", hasta=fin_c)
    s.pon(foto(M / "diego_uruguay_piso.jpg", 400, seed=76), 620, 540, w(17.45), rot=-1.5, nombre="diego_final")
    s.pon(foto(M / "maradona_italia.jpg", 560, seed=77), 1400, 430, w(17.6), rot=2, nombre="diego_capitan",
          sonido=PAPEL)
    s.pon(etiqueta("¿PARA BIEN O PARA MAL?", 40), 1400, 780, w(19.3), rot=-1.5, nombre="bien_mal", sonido=PAPEL)
    return s, [(0, 1.0, W / 2, H / 2), (w(5.7), 1.0, W / 2, H / 2), (w(6.8), 1.3, 1000, 430),
               (w(8.5), 1.3, 1000, 430), (w(8.8), 1.0, W / 2, H / 2), (w(17.3), 1.03, W / 2, H / 2),
               (w(17.4), 1.0, W / 2, H / 2), (23.0, 1.05, 900, 540)]


# ───────────── capítulo 2: El grupo (Corea, Italia, Bulgaria) ─────────────
VOCES_C2 = ["0a82ddb83269d851", "e8d2c6b381b11b4c", "cb234590bbc01d2b", "0cc535682001f14d"]
FB_REC = (0, 110, 1540, 920)        # videos de Football Flashback: sin reloj/marcador agregado, logo ni texto de abajo
IT_REC = (0, 170, 1920, 920)        # Italia: hace falta el arco de la derecha (el logo queda arriba de y=150)
COREA, ITALIA, BULGARIA = (M / f"fuentes/{n}.mp4" for n in ("corea", "italia", "bulgaria"))
TIZA = {"archivo": "papel3", "vol": 0.25, "dur": 0.4}     # 18/11: "sacá todas las tizas" (también el sonido)


def en_foto(X, Y, rec, alto, px, py):
    """Punto (px, py) del cuadro original -> pantalla, para una foto(.., alto, caja=rec) pegada en (X, Y) sin rotar."""
    s = alto / (rec[3] - rec[1])
    return X + (px - (rec[0] + rec[2]) / 2) * s, Y + (py - (rec[1] + rec[3]) / 2) * s


def palote(alto=120, diagonal=False, seed=0):
    """Una raya de conteo a mano (o la diagonal que cierra el grupo de cinco)."""
    rng = np.random.default_rng(seed)
    w_ = 230 if diagonal else 40
    im = Image.new("RGBA", (w_, alto + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if diagonal:
        d.line([(8, alto + 6), (w_ - 8, 14)], fill=ROJO + (240,), width=11)
    else:
        x = 20 + rng.uniform(-3, 3)
        d.line([(x, 10), (x + rng.uniform(-5, 5), alto + 8)], fill=TINTA_T + (245,), width=10)
    return im


def trayecto(puntos, grosor=8, guion=26, punta=False):
    """Línea roja punteada por varios puntos (en pantalla); devuelve (img, cx, cy). 18/11: sin punta de flecha por
    defecto (pedido del usuario: "sacá las flechas")."""
    xs, ys = [p[0] for p in puntos], [p[1] for p in puntos]
    x0, y0 = min(xs) - 40, min(ys) - 40
    im = Image.new("RGBA", (int(max(xs) - x0 + 40), int(max(ys) - y0 + 40)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(x - x0, y - y0) for x, y in puntos]
    seg = []
    for (a, b), (c, e) in zip(pts, pts[1:]):
        n = max(2, int(np.hypot(c - a, e - b) / 4))
        seg += [(a + (c - a) * k / n, b + (e - b) * k / n) for k in range(n)]
    for k in range(0, len(seg) - 1, 2 * guion // 4):
        d.line(seg[k:k + guion // 4 + 1], fill=ROJO + (240,), width=grosor)
    if punta:
        (a, b), (c, e) = pts[-2], pts[-1]
        ang = np.arctan2(e - b, c - a)
        for da in (2.6, -2.6):
            d.line([(c, e), (c + 34 * np.cos(ang + da), e + 34 * np.sin(ang + da))], fill=ROJO + (240,), width=grosor)
    im.info["dibujo"] = True
    return im, x0 + im.width / 2, y0 + im.height / 2


def tabla(filas, tam=64, seed=80):
    """Tabla en recorte de diario; devuelve (img, dy de la primera fila respecto del centro, ancho de esa fila)."""
    im = diario("\n".join(filas), 640, tam, arriba="MÉXICO 86 · GRUPO A · TABLA FINAL", seed=seed)
    alto = len(filas) * int(tam * 1.2) + int(tam * 0.9) + int(tam * 1.8) + 28
    fila1 = 14 + tam * 0.85 + tam * 0.9 + tam * 0.6
    ancho = ImageDraw.Draw(Image.new("L", (1, 1))).textlength(filas[0], font=plex(tam, 600))
    return im, fila1 - alto / 2, ancho, im.width


def c2_1():
    """Primer partido, Olímpico Universitario: Corea del Sur. El plan: pegarle. Lo patearon once veces en 90 minutos."""
    s = Escena("p3_1", 13.8)
    s.pon(etiqueta("PRIMER PARTIDO · 2 DE JUNIO DE 1986", 30), 560, 150, w(0.1), rot=-1.5, nombre="primer_partido",
          hasta=w(4.9))
    s.clip(5.5, w(0.3), w(4.9), ancho=1000, x=640, y=560, rot=-1, nombre="clip_salida_corea", src=COREA, rec=FB_REC)
    s.pon(etiqueta("ESTADIO OLÍMPICO UNIVERSITARIO", 30), 1480, 330, w(1.3), rot=1.5, nombre="estadio", hasta=w(4.9))
    s.pon(marcador("ARG  vs  COR", "GRUPO A · CIUDAD DE MÉXICO", seed=81), 1480, 600, w(3.2), rot=-2,
          nombre="vs_corea", entrada="golpe", dura=0.1, sonido=SELLO, hasta=w(4.9))
    # "esperaban a Diego con un solo plan... ¡pegarle!": el clip corre lento y se congela cuando lo voltean
    s.clip(9.0 - (w(8.3) - w(5.0)) * 0.4, w(5.0), w(8.35), ancho=1050, x=700, y=580, rot=1, vel=0.4,
           nombre="clip_patada_corea", src=COREA, rec=FB_REC)
    s.pon(foto(M / "congelados/corea_patada1.png", 600, caja=FB_REC, seed=82), 700, 580, w(8.3), rot=1,
          nombre="congelado_corea1", entrada="golpe", dura=0.12, sonido=CONGELA)
    cx, cy = en_foto(700, 580, FB_REC, 600, 1080, 800)       # Diego en el piso
    s.pon(circulo(300, 240, seed=5), cx, cy, w(8.5), nombre="circulo_diego_corea", entrada="trazo", dura=0.35)
    s.pon(C.sello("¡PEGARLE!", tam=100, rot=-6, seed=83), 1480, 420, w(8.3), nombre="pegarle", entrada="golpe",
          dura=0.08, sonido=SELLO, hasta=w(9.2))
    # "lo patearon once veces": la segunda patada congelada y el conteo a mano, una raya por falta
    s.pon(foto(M / "congelados/corea_patada2.png", 300, caja=FB_REC, seed=84), 1500, 250, w(9.3), rot=3,
          nombre="congelado_corea2", sonido=PAPEL)
    for k in range(11):
        grupo, j = divmod(k, 5)
        x0 = 1250 + grupo * 250
        if j < 4 or k == 10:
            s.pon(palote(130, seed=k), x0 + (j if k < 10 else 0) * 46, 640, w(9.5) + k * 0.13, nombre=f"falta{k + 1:02d}",
                  entrada="aparece", dura=0.08, sonido=TIZA)
        else:
            s.pon(palote(130, diagonal=True), x0 + 70, 640, w(9.5) + k * 0.13, nombre=f"falta{k + 1:02d}",
                  entrada="trazo", dura=0.12, sonido=TIZA)
    s.pon(titulo("11 faltas\nen 90 minutos", 76), 1480, 870, w(10.5), nombre="once_faltas")
    return s, [(0, 1.0, W / 2, H / 2), (w(4.9), 1.0, W / 2, H / 2), (w(8.3), 1.0, W / 2, H / 2),
               (w(9.2), 1.08, 760, 600), (w(9.3), 1.0, W / 2, H / 2), (13.8, 1.05, 1300, 640)]


def c2_2():
    """Argentina ganó 3 a 1: dos goles de Valdano y uno de Ruggeri. Los tres, con pase de Diego."""
    s = Escena("p3_2", 10.2)
    s.clip(51.0 - (w(2.6) - w(0.0)) * 0.6, w(0.0), w(4.5), ancho=1050, x=700, y=560, rot=-1, nombre="gol_valdano",
           src=COREA, rec=FB_REC)
    s.pon(marcador("3 - 1", "ARG · COR", seed=85), 1520, 330, w(1.3), rot=2, nombre="m31", entrada="golpe",
          dura=0.1, sonido=SELLO, hasta=w(4.5))
    s.pon(etiqueta("VALDANO 6' · RUGGERI 18' · VALDANO 46'", 26), 1520, 520, w(2.5), rot=-1, nombre="goleadores",
          hasta=w(4.5))
    s.pon(etiqueta("PARK CHANG-SUN 73'", 22), 1520, 580, w(2.9), rot=1, nombre="descuento", hasta=w(4.5))
    s.pon(foto(M / "valdano_festejo.jpg", 400, seed=86), 400, 470, w(4.6), rot=-2, nombre="valdano")   # las fotos eg_ son de la final
    s.pon(etiqueta("VALDANO · 2 GOLES", 30), 400, 770, w(4.7), rot=1, nombre="valdano_tira")
    s.pon(foto(M / "ruggeri_festejo.jpg", 360, seed=87), 1520, 470, w(4.6), rot=2, nombre="ruggeri")
    s.pon(etiqueta("RUGGERI · 1 GOL", 30), 1520, 770, w(4.9), rot=-1, nombre="ruggeri_tira")
    s.pon(foto(M / "diego_corea.jpg", 320, seed=88), W / 2, 820, w(6.5), nombre="diego_pases")
    for k, (a, b) in enumerate([((840, 760), (600, 560)), ((1080, 760), (1330, 560))]):
        im, cx, cy = trayecto([a, ((a[0] + b[0]) / 2, b[1] + 60), b], grosor=7)
        s.pon(im, cx, cy, w(6.9 + 0.25 * k), nombre=f"pase{k + 1}", entrada="trazo", dura=0.4,
              sonido=PAPEL if k == 0 else False)
    return s, [(0, 1.0, W / 2, H / 2), (w(4.5), 1.0, W / 2, H / 2), (10.2, 1.05, W / 2, 600)]


def c2_3():
    """Puebla, el campeón del mundo: Italia. Altobelli de penal 1-0; Maradona casi sin ángulo, de zurda: 1-1."""
    s = Escena("p3_3", 12.8)
    s.pon(etiqueta("PUEBLA · 5 DE JUNIO", 30), 520, 150, w(0.6), rot=-1.5, nombre="puebla", hasta=w(3.3))
    s.pon(foto(M / "italia_campeon82.jpg", 520, seed=88), 640, 560, w(1.6), rot=-1.5, nombre="italia_82",
          sonido=PAPEL, hasta=w(3.3))
    s.pon(marcador("ITALIA", "CAMPEÓN EN ESPAÑA 82", seed=89), 1420, 500, w(2.6), rot=2, nombre="italia",
          entrada="golpe", dura=0.1, sonido=SELLO, hasta=w(3.3))
    s.clip(61.0 - (w(5.75) - w(3.4)) * 0.6, w(3.4), w(6.8), ancho=1050, x=700, y=560, rot=1, nombre="penal_altobelli",
           src=ITALIA, rec=IT_REC)
    s.pon(etiqueta("ALTOBELLI · PENAL", 30), 1520, 300, w(3.6), rot=-1, nombre="altobelli", hasta=w(6.8))
    s.pon(marcador("0 - 1", "ARG · ITA  —  ALTOBELLI 6'", seed=90), 1520, 560, w(5.8), rot=2, nombre="m01",
          entrada="golpe", dura=0.1, sonido=SELLO, hasta=w(6.8))
    # el gol de Diego: corre, se congela en el remate y se dibuja el ángulo y la pelota
    X, Y, AL = 820, 560, 660
    s.clip(270.9 - (w(8.0) - w(6.9)) * 0.6, w(6.9), w(8.05), ancho=int(AL * 1920 / 750), x=X, y=Y, nombre="gol_diego",
           src=ITALIA, rec=IT_REC)
    s.pon(foto(M / "congelados/italia_angulo.png", AL, caja=IT_REC, seed=91), X, Y, w(8.0), nombre="congelado_italia",
          entrada="golpe", dura=0.12, sonido=CONGELA)
    dx, dy = en_foto(X, Y, IT_REC, AL, 994, 390)
    s.pon(circulo(150, 170, grosor=7, seed=6), dx, dy, w(8.15), nombre="circulo_diego_italia", entrada="trazo",
          dura=0.3)
    im, cx, cy = trayecto([en_foto(X, Y, IT_REC, AL, *p) for p in ((1010, 440), (1404, 572), (1690, 600))])
    s.pon(im, cx, cy, w(8.4), nombre="trayecto_pelota", entrada="trazo", dura=0.5)
    s.pon(C.sello("CASI SIN ÁNGULO", tam=64, rot=-5, seed=92), 560, 190, w(8.0), nombre="sin_angulo",
          entrada="golpe", dura=0.08, sonido=SELLO)
    s.pon(etiqueta("DE ZURDA", 40, fondo=ROJO), dx, dy + 150, w(9.0), rot=2, nombre="zurda", entrada="golpe",
          dura=0.1, sonido=PAPEL)
    s.pon(marcador("1 - 1", "MARADONA 34'", seed=93), 1640, 880, w(9.6), rot=-2, nombre="m11_italia",
          entrada="golpe", dura=0.1, sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (w(8.0), 1.0, W / 2, H / 2), (w(9.2), 1.1, 1000, 560),
               (12.8, 1.12, 1050, 580)]


def c2_4():
    """Bulgaria 2-0 (Valdano y Burruchaga). Primera del grupo, sin perder. Y sin que nadie todavía se asustara."""
    s = Escena("p3_4", 13.4)
    s.pon(etiqueta("10 DE JUNIO · CIUDAD DE MÉXICO", 28), W / 2, 1035, w(0.4), rot=-1, nombre="bulgaria_fecha",
          hasta=w(5.3))
    goles_juntos(s, [dict(desde=28.5 - (w(3.6) - w(0.6)) * 0.6, t=w(0.6), src=BULGARIA, rec=FB_REC, vel=0.6,
                          nombre="gol_valdano_bul", texto="ARG 1-0 BUL", sub="VALDANO 4'", t_marca=w(3.5)),
                     dict(desde=443.0 - (w(4.6) - w(3.9)) * 0.6, t=w(3.9), src=BULGARIA, rec=FB_REC, vel=0.6,
                          nombre="gol_burru", texto="ARG 2-0 BUL", sub="BURRUCHAGA 77'", t_marca=w(4.0))],
                 hasta=w(5.3))
    # la tabla del grupo
    tb, dy1, a1, wt = tabla(["1. Argentina · 5 pts", "2. Italia · 4 pts", "3. Bulgaria · 2 pts",
                             "4. Corea del Sur · 1 pt"])
    s.pon(tb, 700, 560, w(5.4), nombre="tabla", sonido=PAPEL, hasta=w(7.3))
    s.pon(circulo(int(a1 + 60), 110, seed=7), 700 - wt / 2 + 14 + 64 * 0.8 + a1 / 2, 560 + dy1 + 8, w(5.6), nombre="circulo_primero", entrada="trazo", dura=0.4,
          hasta=w(7.3))
    s.pon(C.sello("INVICTO", tam=120, rot=-7, seed=95), 1500, 560, w(6.5), nombre="invicto", entrada="golpe",
          dura=0.08, sonido=SELLO, hasta=w(7.3))
    s.pon(foto(M / "entrenamiento.jpg", 600, seed=97), 760, 500, w(7.5), rot=-1.5, nombre="entrenamiento_solo",
          sonido=PAPEL)
    s.pon(C.sello("TODAVÍA", tam=110, rot=-5, seed=96), 1250, 720, w(8.6), nombre="todavia", entrada="golpe",
          dura=0.08, sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (w(7.3), 1.0, W / 2, H / 2), (13.4, 1.07, 1100, 560)]


CAPITULO2 = [c2_1, c2_2, c2_3, c2_4]


# ───────────── capítulo 3: Las camisetas (Uruguay, el calor, Moschella y la tienda) ─────────────
VOCES_C3 = ["40c1e4ce56cd18d7", "7341d25281155286", "72bd3529157f4ca6", "f9860afef21b041c"]   # guion_j 16-19
URUGUAY = M / "fuentes/uruguay.mp4"
COL = M / "collage"
PESA = {"archivo": str(RAIZ / ".cache/elevenlabs/sfx_6cf1b19cf8033e97.mp3"), "vol": 0.6, "dur": 1.2}
VAPOR = {"archivo": str(RAIZ / ".cache/elevenlabs/sfx_77d62f151b33360b.mp3"), "vol": 0.5, "dur": 1.0}
ING_ESCUDO = (700, 120, 1500, 760)          # ing_229.5: Diego de frente, sin el marcador (spoiler) ni el zócalo de la TV
ING_NUMERO = (0, 130, 1500, 780)            # ing_365.5: el 10 plateado en la espalda


def c3_1():
    """Octavos, Puebla, el clásico del Río de la Plata: Uruguay. Trabado, cerrado; lo definió Pasculli antes del
    entretiempo. 1 a 0."""
    s = Escena("p4_1", 13.8)
    s.pon(etiqueta("OCTAVOS DE FINAL · 16 DE JUNIO", 30), 560, 140, w(0.1), rot=-1.5, nombre="octavos", hasta=w(5.5))
    s.clip(13.6, w(0.2), w(5.5), ancho=1000, x=640, y=580, rot=-1, vel=0.5, nombre="clip_salida_uruguay",
           src=URUGUAY, rec=FB_REC)
    s.pon(etiqueta("ESTADIO CUAUHTÉMOC · PUEBLA", 30), 1480, 290, w(1.5), rot=1.5, nombre="puebla_c3", hasta=w(5.5))
    s.pon(foto(M / "intro/banderas/argentina.png", 150, seed=99), 1380, 540, w(2.4), rot=-3, nombre="bandera_arg_uru",
          sonido=PAPEL, hasta=w(5.5))
    s.pon(foto(M / "intro/banderas/uruguay.png", 150, seed=100), 1600, 550, w(2.7), rot=3, nombre="bandera_uru",
          sonido=PAPEL, hasta=w(5.5))
    s.pon(marcador("ARG  vs  URU", "OCTAVOS · PUEBLA", seed=101), 1480, 820, w(4.56), rot=-2, nombre="vs_uruguay",
          entrada="golpe", dura=0.1, sonido=SELLO, hasta=w(5.5))
    # trabado, cerrado: la pila de jugadores en el piso
    s.clip(11.8, w(5.6), w(8.4), ancho=1050, x=740, y=560, rot=1, vel=0.5, nombre="clip_trabado", src=URUGUAY,
           rec=FB_REC)
    s.pon(C.sello("TRABADO", tam=96, rot=-6, seed=102), 1530, 360, w(5.64), nombre="trabado", entrada="golpe",
          dura=0.08, sonido=SELLO, hasta=w(8.4))
    s.pon(C.sello("CERRADO", tam=96, rot=4, seed=103), 1530, 680, w(6.75), nombre="cerrado", entrada="golpe",
          dura=0.08, sonido=SELLO, hasta=w(8.4))
    # el gol de Pasculli y el festejo congelado
    s.clip(237.5 - (w(11.55) - w(8.4)) * 0.6, w(8.4), w(12.2), ancho=1100, x=700, y=560, rot=-1, nombre="gol_pasculli_uru",
           src=URUGUAY, rec=FB_REC)
    s.pon(etiqueta("PEDRO PASCULLI", 34, fondo=ROJO), 1560, 250, w(8.5), rot=-1.5, nombre="pasculli", sonido=PAPEL)
    s.pon(etiqueta("ANTES DEL ENTRETIEMPO · 42'", 28), 1560, 360, w(9.4), rot=1, nombre="entretiempo")
    s.pon(foto(M / "congelados/uru_pasculli.png", 520, caja=FB_REC, seed=104), 700, 560, w(12.15), rot=1.5,
          nombre="pasculli_festejo", entrada="golpe", dura=0.12, sonido=CONGELA)
    s.pon(marcador("1 - 0", "ARG · URU  —  PASCULLI 42'", seed=105), 1440, 720, w(11.52), rot=2, nombre="m10_uru",
          entrada="golpe", dura=0.1, sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (w(8.4), 1.0, W / 2, H / 2), (13.8, 1.04, W / 2, H / 2)]


def c3_2():
    """Ese partido dejó un problema: camisetas azules de algodón, gruesas; con el calor de México pesaban una
    tonelada. Los jugadores terminaron empapados."""
    s = Escena("p4_2", 13.6)
    s.clip(31.0, w(0.0), w(2.6), ancho=1050, x=W / 2, y=540, rot=-1.5, vel=0.5, nombre="azul_uruguay", src=URUGUAY,
           rec=FB_REC)
    # la camiseta: el 10 de espaldas, corre lento y se congela; círculo sobre la tela
    X, Y, AL = 760, 560, 640
    s.clip(34.68 - (w(4.5) - w(2.6)) * 0.4, w(2.6), w(4.55), ancho=int(AL * 1540 / 810), x=X, y=Y, vel=0.4,
           nombre="clip_camiseta_azul", src=URUGUAY, rec=FB_REC)
    s.pon(foto(M / "congelados/uru_camiseta.png", AL, caja=FB_REC, seed=106), X, Y, w(4.5), nombre="congelado_camiseta",
          entrada="golpe", dura=0.12, sonido=CONGELA, hasta=w(6.5))
    cx, cy = en_foto(X, Y, FB_REC, AL, 700, 560)
    s.pon(circulo(330, 380, seed=8), cx, cy, w(4.7), nombre="circulo_tela", entrada="trazo", dura=0.35, hasta=w(6.5))
    s.pon(etiqueta("CAMISETA AZUL", 34, fondo=ROJO), 1600, 300, w(3.4), rot=-1.5, nombre="azul", hasta=w(6.5))
    s.pon(etiqueta("100 % ALGODÓN", 34), 1600, 470, w(4.6), rot=1.5, nombre="algodon", sonido=PAPEL, hasta=w(6.5))
    s.pon(C.sello("GRUESAS", tam=90, rot=-5, seed=107), 1600, 700, w(5.35), nombre="gruesas", entrada="golpe",
          dura=0.08, sonido=SELLO, hasta=w(6.5))
    # el calor y la tonelada: el termómetro, Diego doblado y la pesa que le cae encima
    fin_b = w(9.8)
    s.pon(sin_blanco(COL / "termometro.png", 820, seed=108), 400, 540, w(6.55), rot=-2, nombre="termometro",
          sonido=PAPEL, hasta=fin_b)
    s.pon(etiqueta("EL CALOR DE MÉXICO", 30, fondo=ROJO), 400, 980, w(7.0), rot=1.5, nombre="calor", hasta=fin_b)
    s.pon(foto(M / "congelados/uru_diego_agachado.png", 600, caja=FB_REC, seed=109), 1220, 600, w(7.4), rot=1,
          nombre="diego_agachado", hasta=fin_b)
    s.pon(sin_blanco(COL / "pesa_ton.png", 330, seed=110), 1300, -300, w(7.9), rot=-4, nombre="pesa", entrada="corte",
          dura=0.1, mov=[(w(7.9), w(8.15), 0, 700, "lineal", 0)], sonido=False, hasta=fin_b)
    s.pon(etiqueta("PESABAN UNA TONELADA", 34), 1220, 960, w(8.4), rot=-1, nombre="tonelada", sonido=PESA,
          hasta=fin_b)
    # empapados: al final, doblados
    s.clip(451.4, w(9.8), 13.6, ancho=1100, x=760, y=560, rot=-1, vel=0.4, nombre="clip_empapados", src=URUGUAY,
           rec=FB_REC)
    s.pon(etiqueta("MINUTO 79", 30), 1560, 230, w(10.0), rot=2, nombre="minuto79")
    s.pon(C.sello("EMPAPADOS", tam=100, rot=-6, seed=111), 1380, 840, w(10.97), nombre="empapados", entrada="golpe",
          dura=0.08, sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (w(8.1), 1.0, W / 2, H / 2), (w(9.6), 1.08, 1220, 520),
               (w(9.8), 1.0, W / 2, H / 2), (13.6, 1.05, 900, 560)]


def c3_3():
    """En cuartos, Inglaterra, que se vestía de blanco. A tres días, Bilardo mandó a Rubén Moschella a recorrer los
    negocios de la Ciudad de México. A buscar camisetas... en una tienda."""
    s = Escena("p4_3", 15.4)
    fin_a = w(3.9)
    s.pon(etiqueta("CUARTOS DE FINAL", 34), 560, 130, w(0.15), rot=-1.5, nombre="cuartos", hasta=fin_a)
    s.pon(foto(COL / "ing_323.png", 700, caja=(733, 150, 1566, 960), seed=112), 560, 580, w(0.9), rot=-1.5,
          nombre="ingles_blanco", hasta=fin_a)
    s.pon(etiqueta("INGLATERRA", 36, fondo=ROJO), 560, 960, w(1.0), rot=1, nombre="inglaterra", sonido=PAPEL,
          hasta=fin_a)
    fin_b = w(5.05)
    s.pon(etiqueta("19 DE JUNIO DE 1986", 56), W / 2, 330, w(3.96), rot=-2, nombre="fecha_c3", entrada="golpe",
          dura=0.1, sonido=PAPEL, hasta=fin_b)
    s.pon(C.sello("FALTAN 3 DÍAS", tam=110, rot=-5, seed=113), W / 2, 600, w(4.3), nombre="tres_dias",
          entrada="golpe", dura=0.08, sonido=SELLO, hasta=fin_b)
    # Bilardo -> Moschella (no hay foto suya: ficha en un recorte de diario)
    fin_c = w(8.1)
    s.pon(foto(M / "eg_bilardo86.jpg", 640, caja=(4, 0, 546, 729), seed=114), 470, 540, w(5.14), rot=-1.5,
          nombre="bilardo_c3", hasta=fin_c)
    s.pon(etiqueta("CARLOS BILARDO · DT", 30), 470, 900, w(5.4), rot=1, nombre="bilardo_c3_nombre", hasta=fin_c)
    # (18/11: sin flecha)
    s.pon(diario("Rubén Moschella", 560, 62, resaltar=True, arriba="COLABORADOR DEL CUERPO TÉCNICO", seed=115),
          1440, 470, w(7.0), rot=2, nombre="moschella", sonido=PAPEL, hasta=fin_c)
    s.pon(etiqueta("MISIÓN: CONSEGUIR CAMISETAS", 28, fondo=ROJO), 1440, 700, w(7.6), rot=-1.5,
          nombre="mision", hasta=fin_c)
    # a recorrer los negocios: tres calles del DF unidas por una ruta punteada
    fin_d = w(11.3)
    calles = [("df86_calle3.jpg", (0, 8, 823, 528), 420, 330, 400, 8.18), ("df86_calle1.jpg", (0, 16, 529, 721), 980, 600, 500, 9.06),
              ("df86_calle2.jpg", (0, 3, 817, 539), 1520, 350, 380, 9.73)]
    for k, (f, caja, x, y, al, t) in enumerate(calles):
        s.pon(foto(M / f, al, caja=caja, seed=116 + k), x, y, w(t), rot=(-1) ** k * 1.8, nombre=f"calle{k + 1}",
              sonido=PAPEL, hasta=fin_d)
    im, cx, cy = trayecto([(560, 470), (760, 640), (840, 600)])
    s.pon(im, cx, cy, w(8.7), nombre="ruta1", entrada="trazo", dura=0.4, hasta=fin_d)
    im, cx, cy = trayecto([(1150, 520), (1300, 470), (1380, 420)])
    s.pon(im, cx, cy, w(9.5), nombre="ruta2", entrada="trazo", dura=0.4, hasta=fin_d)
    s.pon(etiqueta("CIUDAD DE MÉXICO · 1986", 30), 1000, 960, w(9.9), rot=-1, nombre="cdmx", hasta=fin_d)
    # a buscar camisetas... en una tienda
    s.pon(sin_blanco(COL / "tienda.png", 620, seed=119), W / 2, 620, w(11.9), nombre="tienda", sonido=PAPEL)
    s.pon(C.sello("EN UNA TIENDA", tam=90, rot=-6, seed=120), 1280, 920, w(12.6), nombre="en_una_tienda",
          entrada="golpe", dura=0.08, sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (w(11.3), 1.0, W / 2, H / 2), (15.4, 1.08, W / 2, 640)]


def c3_4():
    """Volvió con dos modelos; Maradona eligió uno: con esta le ganamos a Inglaterra. Compraron 38, les cosieron el
    escudo y les plancharon números plateados, de los del fútbol americano. La camiseta de la foto más famosa."""
    s = Escena("p4_4", 19.8)
    fin_a = w(6.3)
    lisa = COL / "camiseta_lisa.png"
    s.pon(sin_blanco(lisa, 520, seed=121), 640, 590, w(0.6), rot=-3, nombre="modelo1", sonido=PAPEL, hasta=w(2.8))
    s.pon(etiqueta("MODELO 1", 30), 640, 900, w(0.7), rot=1, nombre="modelo1_tira", hasta=w(2.8))
    s.pon(sin_blanco(lisa, 520, seed=122), 1300, 590, w(0.9), rot=3, nombre="modelo2", sonido=PAPEL, hasta=fin_a)
    s.pon(etiqueta("MODELO 2", 30), 1300, 900, w(1.0), rot=-1, nombre="modelo2_tira", hasta=fin_a)
    s.pon(circulo(560, 600, seed=9), 1300, 590, w(2.3), nombre="circulo_modelo", entrada="trazo", dura=0.4,
          hasta=fin_a)
    s.pon(foto(M / "diego_bulgaria2.jpg", 360, seed=123), 560, 430, w(3.0), rot=-2, nombre="diego_elige", hasta=fin_a)
    s.pon(diario("«Con esta le ganamos\na Inglaterra»", 600, 46, resaltar=True, arriba="MARADONA", seed=124),
          560, 800, w(3.9), rot=-1.5, nombre="cita_diego", sonido=PAPEL, hasta=fin_a)
    # compraron 38: una camisetita por cada una
    fin_b = w(7.6)
    chica = sin_blanco(lisa, 92, seed=125)
    for k in range(38):
        fila, col = divmod(k, 10)
        s.pon(chica, 330 + col * 140, 200 + fila * 130, w(6.4) + k * 0.025, rot=(k % 5 - 2) * 2.5,
              nombre=f"camiseta{k + 1:02d}", dura=0.15, sonido=TIZA if k % 6 == 0 else False, hasta=fin_b)
    s.pon(titulo("38 camisetas", 120), W / 2, 880, w(7.03), nombre="treinta_y_ocho", entrada="golpe", dura=0.1,
          sonido=SELLO, hasta=fin_b)
    # el escudo cosido
    fin_c = w(9.3)
    X, Y, AL = 720, 540, 640
    s.pon(foto(COL / "ing_229.5.png", AL, caja=ING_ESCUDO, seed=126), X, Y, w(7.62), rot=-1, nombre="escudo_foto",
          hasta=fin_c)
    s.pon(sin_blanco(COL / "aguja.png", 420, seed=127), 1450, 430, w(7.9), rot=-8, nombre="aguja", sonido=PAPEL,
          hasta=fin_c)
    ex, ey = en_foto(X, Y, ING_ESCUDO, AL, 1160, 350)
    s.pon(circulo(170, 170, grosor=8, seed=10), ex, ey, w(8.6), nombre="circulo_escudo", entrada="trazo", dura=0.3,
          hasta=fin_c)
    s.pon(etiqueta("ESCUDO DE LA AFA · COSIDO", 30, fondo=ROJO), 1450, 800, w(8.75), rot=1.5, nombre="escudo_tira",
          hasta=fin_c)
    # los números plateados, planchados
    fin_d = w(12.3)
    X, Y, AL = 760, 520, 600
    s.pon(foto(COL / "ing_365.5.png", AL, caja=ING_NUMERO, seed=128), X, Y, w(9.34), rot=1, nombre="numero_foto",
          hasta=fin_d)
    s.pon(sin_blanco(COL / "plancha.png", 300, seed=129), 1620, 280, w(9.5), rot=-4, nombre="plancha",
          mov=[(w(9.6), w(10.2), -140, 30, "s", 0), (w(10.2), w(10.8), 140, -30, "s", 0)], sonido=VAPOR, hasta=fin_d)
    nx, ny = en_foto(X, Y, ING_NUMERO, AL, 700, 430)
    s.pon(circulo(760, 440, seed=11), nx, ny, w(10.3), nombre="circulo_numero", entrada="trazo", dura=0.4,
          hasta=fin_d)
    s.pon(etiqueta("NÚMEROS PLATEADOS", 36, fondo=ROJO), 1500, 900, w(10.5), rot=-1.5, nombre="plateados",
          sonido=PAPEL, hasta=fin_d)
    # como en el fútbol americano
    fin_e = w(14.6)
    s.pon(foto(COL / "ing_365.5.png", 380, caja=ING_NUMERO, seed=130), 540, 500, w(12.36), rot=-1.5,
          nombre="numero_chico", hasta=fin_e)
    s.pon(sin_blanco(COL / "futbol_americano.png", 760, seed=131), 1480, 520, w(12.6), rot=2,
          nombre="futbol_americano", sonido=PAPEL, hasta=fin_e)
    s.pon(titulo("=", 180, resaltar=False), 1080, 470, w(13.0), nombre="igual", hasta=fin_e)
    s.pon(etiqueta("COMO EN EL FÚTBOL AMERICANO", 34), W / 2, 960, w(13.2), rot=-1, nombre="americano", hasta=fin_e)
    # la foto más famosa del siglo
    X, Y, AL = W / 2, 520, 820
    s.pon(foto(M / "mano_dios2.jpg", AL, seed=132), X, Y, w(14.7), rot=-1, nombre="foto_del_siglo", sonido=PAPEL)
    s.pon(circulo(200, 300, seed=12), X + (650 - 1133 / 2) * AL / 823, Y + (310 - 823 / 2) * AL / 823, w(15.3),
          nombre="circulo_camiseta", entrada="trazo", dura=0.4)
    s.pon(C.sello("LA FOTO DEL SIGLO", tam=80, rot=-5, seed=133), 1250, 900, w(17.1), nombre="foto_siglo",
          entrada="golpe", dura=0.08, sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (w(14.6), 1.0, W / 2, H / 2), (19.8, 1.1, 1030, 470)]


CAPITULO3 = [c3_1, c3_2, c3_3, c3_4]


# ───────────── capítulo 4: La guerra (Malvinas, Rattín 66, el Azteca, el primer tiempo) ─────────────
VOCES_C4 = ["3b879db30fe787e1", "97a9d4c2074fe58e", "35794b41895b847d", "fa7c794b871522b1",
            "e02fb8be52b34aff"]   # guion_j 21-25
BAN = M / "intro/banderas"
RATTIN = M / "fuentes/rattin1966.mp4"
RAT_REC = (60, 0, 1040, 720)                # sin el logo de DeporTV (arriba a la derecha)
RAT_REC2 = (0, 110, 1280, 720)
ING1 = M / "fuentes/inglaterra_completo.mp4"
ING1_REC = (0, 130, 975, 720)               # sin "ARG 0-0 ENG", el logo de FIFA TV ni la columna de formaciones
SOBRIO = {"archivo": "papel1", "vol": 0.35}
GRAVE = {"archivo": "whoosh_grave", "vol": 0.55}


def c4_1():
    """No era un partido más. Cuatro años antes, la guerra. ¿Por qué? Malvinas: islas en el Atlántico Sur, a unos
    500 km de la costa patagónica. Inglaterra las ocupa desde 1833 y Argentina siempre las reclamó."""
    import globo
    s = Escena("p5_1", 21.7)
    # "No era un partido más": la tapa del día del partido (Valdano vs. Stevens), no el texto repetido
    s.pon(foto(M / "diario_previa_mundial.jpg", 800, caja=(0, 0, 689, 560), seed=139), W / 2, 540, w(0.0), rot=-2,
          nombre="diario_previa", sonido=PAPEL, hasta=w(2.5))
    s.pon(etiqueta("MONTEVIDEO · 22 DE JUNIO DE 1986", 30), W / 2 + 330, 930, w(0.4), rot=2, nombre="diario_fecha",
          hasta=w(2.5))
    fin_a = w(6.9)
    s.pon(etiqueta("CUATRO AÑOS ANTES · 1982", 34), W / 2, 170, w(2.62), rot=-1.5, nombre="cuatro_anios",
          sonido=PAPEL, hasta=fin_a)
    s.pon(foto(BAN / "argentina.png", 330, seed=140), 600, 520, w(3.6), rot=-3, nombre="bandera_arg",
          sonido=SOBRIO, hasta=fin_a)
    s.pon(foto(BAN / "england.png", 330, seed=141), 1320, 520, w(4.38), rot=3, nombre="bandera_ing",
          sonido=SOBRIO, hasta=fin_a)
    s.pon(C.sello("GUERRA", tam=120, rot=-5, seed=142), W / 2, 820, w(5.83), nombre="guerra", entrada="golpe",
          dura=0.08, sonido=SELLO, hasta=fin_a)
    # "¿Por qué? Por las Malvinas": la Tierra en 3D, la cámara baja al Atlántico Sur y se marcan las islas
    g = globo.Globo(pais="Falkland Islands", centro=(-51.5, -64.0), desde_lon=-25, r0=330, r1=7000,
                    t_zoom=(0.2, 1.9), t_marca=2.0, recorte=(-62, -38, -80, -48))
    T = w(6.9)
    s.pon(None, W / 2, H / 2, T, nombre="globo_malvinas", fn=g.cuadro, dura=0.3, sonido=GRAVE)
    xi, yi = g.pantalla(-51.7, -59.0, 3)
    s.pon(etiqueta("ISLAS MALVINAS", 40, fondo=ROJO), xi, yi - 130, w(8.9), rot=-1.5, nombre="islas", sonido=PAPEL)
    s.pon(etiqueta("ATLÁNTICO SUR", 30), 1500, 900, w(9.83), rot=1, nombre="atlantico")
    xc, yc = g.pantalla(-51.6, -68.9, 3)
    xw, yw = g.pantalla(-51.65, -61.0, 3)
    im, cx, cy = C_trayecto([(xc + 30, yc), (xw - 20, yw)])
    s.pon(im, cx, cy, w(11.0), nombre="linea_500km", entrada="trazo", dura=0.6)
    s.pon(etiqueta("≈ 500 KM", 36), (xc + xw) / 2, yc + 90, w(11.27), rot=-1, nombre="500km", sonido=PAPEL)
    s.pon(etiqueta("COSTA PATAGÓNICA", 28), xc - 120, yc + 230, w(12.66), rot=1.5, nombre="patagonia")
    # 1833: la bandera inglesa sobre las islas; Argentina siempre las reclamó
    s.pon(foto(BAN / "england.png", 150, seed=143), xi + 210, yi + 80, w(14.44), rot=6, nombre="bandera_ing_islas",
          sonido=SOBRIO)
    s.pon(C.sello("DESDE 1833", tam=88, rot=-5, seed=144), xi, yi + 270, w(15.78), nombre="desde_1833",
          entrada="golpe", dura=0.08, sonido=SELLO)
    s.pon(foto(BAN / "argentina.png", 170, seed=145), xc - 60, yc - 140, w(17.18), rot=-5, nombre="bandera_arg_costa",
          sonido=SOBRIO)
    s.pon(foto(M / "malv_plaza.jpg", 380, seed=146), 420, 300, w(18.72), rot=-2, nombre="siempre_malvinas",
          sonido=SOBRIO)
    return s, [(0, 1.0, W / 2, H / 2), (w(10.0), 1.0, W / 2, H / 2), (21.7, 1.05, W / 2, 560)]


def C_trayecto(puntos):
    return trayecto(puntos)


def c4_2():
    """Abril de 1982: la dictadura mandó tropas; Inglaterra respondió con su flota. 74 días de guerra. Murieron 649
    soldados argentinos y 255 británicos. Muchos argentinos eran chicos de 18 y 19 años, del servicio militar."""
    s = Escena("p5_2", 23.6)
    fin_a = w(5.6)
    s.pon(etiqueta("2 DE ABRIL DE 1982", 48), W / 2, 140, w(0.22), rot=-1.5, nombre="dos_de_abril", entrada="golpe",
          dura=0.1, sonido=PAPEL, hasta=fin_a)
    s.pon(foto(M / "malv_galtieri.jpg", 640, seed=146), 470, 600, w(2.52), rot=-1.5, nombre="galtieri",
          sonido=SOBRIO, hasta=fin_a)
    s.pon(etiqueta("DICTADURA MILITAR · GALTIERI", 28), 470, 960, w(2.7), rot=1, nombre="dictadura", hasta=fin_a)
    s.pon(foto(M / "malvinas_desembarco.jpg", 500, seed=147), 1300, 560, w(3.82), rot=1.5, nombre="desembarco",
          sonido=SOBRIO, hasta=fin_a)
    s.pon(etiqueta("TROPAS A LAS ISLAS", 30, fondo=ROJO), 1300, 870, w(4.27), rot=-1, nombre="tropas", hasta=fin_a)
    fin_b = w(7.95)
    s.pon(foto(M / "malv_canberra.jpg", 480, seed=148), W / 2, 520, w(5.8), rot=-1, nombre="flota", sonido=SOBRIO,
          hasta=fin_b)
    s.pon(etiqueta("LA FLOTA BRITÁNICA", 36, fondo=ROJO), W / 2, 860, w(6.97), rot=1, nombre="flota_tira",
          hasta=fin_b)
    # 74 días: palotes de a cinco
    fin_c = w(10.7)
    for k in range(74):
        grupo, j = divmod(k, 5)
        fila, col = divmod(grupo, 5)
        x0, y0 = 420 + col * 270, 250 + fila * 190
        t = w(8.2) + k * 0.016
        if j < 4:
            s.pon(palote(120, seed=k), x0 + j * 44, y0, t, nombre=f"dia{k + 1:02d}", dura=0.08, hasta=fin_c,
                  sonido=TIZA if k % 15 == 0 else False)
        else:
            s.pon(palote(120, diagonal=True, seed=k), x0 + 66, y0, t, nombre=f"dia{k + 1:02d}", dura=0.08,
                  hasta=fin_c)
    s.pon(titulo("74 días de guerra", 110), W / 2, 900, w(8.72), nombre="setenta_y_cuatro", hasta=fin_c)
    # los muertos: sin golpes, todo entra tranquilo
    fin_d = w(17.2)
    s.pon(foto(M / "malvinas_soldados2.jpg", 640, seed=149), 520, 560, w(10.86), rot=-1.5, nombre="soldados",
          sonido=SOBRIO, hasta=fin_d)
    s.pon(titulo("649", 190, resaltar=False), 1350, 330, w(11.08), nombre="seiscientos_49", dura=0.8, hasta=fin_d)
    s.pon(etiqueta("SOLDADOS ARGENTINOS", 34, fondo=ROJO), 1350, 480, w(12.4), rot=-1, nombre="argentinos",
          hasta=fin_d)
    s.pon(titulo("255", 150, resaltar=False), 1350, 700, w(14.02), nombre="doscientos_55", dura=0.8, hasta=fin_d)
    s.pon(etiqueta("BRITÁNICOS", 30), 1350, 830, w(15.11), rot=1, nombre="britanicos", hasta=fin_d)
    # chicos de 18 y 19 años
    X, Y, AL = 720, 560, 660
    s.pon(foto(M / "malvinas_darwin.jpg", AL, seed=150), X, Y, w(17.34), rot=-1, nombre="chicos", sonido=SOBRIO)
    for k, (px, py, r) in enumerate([(355, 285, 150), (860, 330, 150)]):
        cx, cy = en_foto(X, Y, (0, 0, 960, 600), AL, px, py)
        s.pon(circulo(int(r * AL / 600), int(r * 1.2 * AL / 600), seed=20 + k), cx, cy, w(18.75) + k * 0.3,
              nombre=f"circulo_chico{k + 1}", entrada="trazo", dura=0.35)
    s.pon(titulo("18 y 19\naños", 120), 1560, 400, w(19.42), nombre="dieciocho")
    s.pon(etiqueta("SERVICIO MILITAR", 34, fondo=ROJO), 1560, 680, w(21.51), rot=1.5, nombre="servicio")
    return s, [(0, 1.0, W / 2, H / 2), (w(17.2), 1.0, W / 2, H / 2), (23.6, 1.06, 820, 520)]


def c4_3():
    """Los jugadores decían que era solo fútbol, pero nadie les creía. Y había una cuenta pendiente desde el 66:
    en Wembley echaron a Rattín, que se negó a irse, y el técnico inglés llamó animales a los argentinos."""
    s = Escena("p5_3", 17.4)
    fin_a = w(4.6)
    for k, (n, x, y) in enumerate([("diego_corea2.jpg", 330, 470), ("valdano_grito.jpg", 640, 560),
                                   ("ruggeri_festejo.jpg", 950, 470)]):
        s.pon(foto(M / n, 280, seed=151 + k), x, y, w(0.1) + k * 0.25, rot=(-1) ** k * 2, nombre=f"jugador_{n.split('.')[0]}",
              sonido=SOBRIO if k == 0 else False, hasta=fin_a)
    s.pon(etiqueta("LOS JUGADORES", 30), 620, 820, w(0.25), rot=-1, nombre="los_jugadores", hasta=fin_a)
    s.pon(diario("«Es solo fútbol»", 620, 64, resaltar=True, seed=154), 1450, 400, w(0.9), rot=1.5,
          nombre="solo_futbol", sonido=PAPEL, hasta=fin_a)
    s.pon(C.sello("NADIE LES CREÍA", tam=84, rot=-5, seed=155), 1450, 720, w(2.98), nombre="nadie_creia",
          entrada="golpe", dura=0.08, sonido=SELLO, hasta=fin_a)
    fin_b = w(9.5)
    s.pon(foto(M / "argentina1966.jpg", 560, seed=155), W / 2, 460, w(5.9), rot=-1.5, nombre="seleccion_66",
          sonido=SOBRIO, hasta=fin_b)
    s.pon(C.sello("1966", tam=130, rot=-6, seed=156), W / 2, 790, w(8.08), nombre="sello_66", entrada="golpe",
          dura=0.08, sonido=SELLO, hasta=fin_b)
    # Wembley: el árbitro lo echa; se congela; se niega a irse
    fin_c = w(13.5)
    X, Y, AL = 640, 540, 680
    s.clip(18.0 + 0.0, w(9.6), w(11.0), ancho=int(AL * (RAT_REC[2] - RAT_REC[0]) / (RAT_REC[3] - RAT_REC[1])), x=X,
           y=Y, vel=0.5, nombre="clip_rattin_echado", src=RATTIN, rec=RAT_REC)
    s.pon(foto(M / "congelados/rattin_echado.png", AL, caja=RAT_REC, seed=157), X, Y, w(10.95), nombre="rattin_congelado",
          entrada="golpe", dura=0.12, sonido=CONGELA, hasta=fin_c)
    cx, cy = en_foto(X, Y, RAT_REC, AL, 720, 330)
    s.pon(circulo(300, 420, seed=13), cx, cy, w(11.1), nombre="circulo_rattin", entrada="trazo", dura=0.35,
          hasta=fin_c)
    s.pon(etiqueta("ANTONIO RATTÍN", 40, fondo=ROJO), 1500, 220, w(10.28), rot=-1.5, nombre="rattin", sonido=PAPEL,
          hasta=fin_c)
    s.pon(etiqueta("WEMBLEY · 1966", 30), 1500, 330, w(10.5), rot=1, nombre="wembley", hasta=fin_c)
    s.clip(38.5, w(11.24), fin_c, ancho=760, x=1480, y=640, rot=2, vel=0.6, nombre="clip_se_nego", src=RATTIN,
           rec=RAT_REC2)
    s.pon(C.sello("SE NEGÓ A IRSE", tam=72, rot=-4, seed=158), 1480, 960, w(11.6), nombre="se_nego",
          entrada="golpe", dura=0.08, sonido=SELLO, hasta=fin_c)
    # "animales"
    s.pon(etiqueta("EL TÉCNICO INGLÉS", 34), W / 2, 260, w(13.6), rot=-1.5, nombre="tecnico_ingles", sonido=PAPEL)
    s.pon(diario("«Animales»", 760, 120, resaltar=True, arriba="ALF RAMSEY · DT DE INGLATERRA · 1966", seed=159),
          W / 2, 580, w(14.52), rot=-1, nombre="animales", entrada="golpe", dura=0.12, sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (w(13.5), 1.0, W / 2, H / 2), (17.4, 1.08, W / 2, 580)]


def c4_4():
    """22 de junio, al mediodía, bajo el sol de México. Estadio Azteca: 114 mil personas. El partido más cargado de
    la historia de los Mundiales."""
    s = Escena("p5_4", 11.6)
    fin_a = w(4.0)
    s.pon(etiqueta("22 DE JUNIO DE 1986", 50), 620, 220, w(0.03), rot=-1.5, nombre="veintidos", entrada="golpe",
          dura=0.1, sonido=PAPEL, hasta=fin_a)
    s.pon(titulo("12:00", 150, resaltar=False), 620, 520, w(1.4), nombre="mediodia", hasta=fin_a)
    s.pon(sin_blanco(COL / "termometro.png", 760, seed=160), 1450, 560, w(2.64), rot=3, nombre="sol_termometro",
          sonido=PAPEL, hasta=fin_a)
    s.pon(etiqueta("EL SOL DE MÉXICO", 32, fondo=ROJO), 1450, 960, w(2.9), rot=-1, nombre="sol", hasta=fin_a)
    fin_b = w(7.85)
    s.pon(foto(M / "azteca_1986.jpg", 600, seed=161), 680, 520, w(4.08), rot=-1.5, nombre="azteca", sonido=SOBRIO,
          hasta=fin_b)
    s.pon(etiqueta("ESTADIO AZTECA", 40, fondo=ROJO), 680, 880, w(4.38), rot=1, nombre="azteca_tira", hasta=fin_b)
    s.pon(titulo("114.000\npersonas", 110), 1500, 330, w(5.04), nombre="ciento_catorce", hasta=fin_b)
    s.pon(foto(M / "congelados/ing1_tribuna.png", 340, caja=ING1_REC, seed=162), 1500, 760, w(6.12), rot=2,
          nombre="tribuna_azteca", sonido=SOBRIO, hasta=fin_b)
    s.pon(foto(M / "saludo_capitanes.jpg", 460, seed=166), W / 2, 380, w(7.77), rot=-1, nombre="saludo_capitanes",
          sonido=SOBRIO)
    s.pon(foto(BAN / "argentina.png", 260, seed=163), 620, 720, w(8.5), rot=-3, nombre="ban_arg_azteca",
          sonido=SOBRIO)
    s.pon(foto(BAN / "england.png", 260, seed=164), 1300, 720, w(8.62), rot=3, nombre="ban_ing_azteca")
    s.pon(marcador("ARG  vs  ING", "CUARTOS · AZTECA", seed=165), W / 2, 760, w(9.68), rot=-2, nombre="vs_ing",
          entrada="golpe", dura=0.1, sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (w(7.6), 1.0, W / 2, H / 2), (11.6, 1.07, W / 2, 600)]


def c4_5():
    """Primer tiempo: 0 a 0. Inglaterra cerraba todos los caminos. Y Diego, cada vez que agarraba la pelota, tenía
    dos ingleses encima."""
    s = Escena("p5_5", 10.0)
    X, Y, AL = 700, 560, 640
    ancho = int(AL * (ING1_REC[2] - ING1_REC[0]) / (ING1_REC[3] - ING1_REC[1]))
    s.pon(marcador("0 - 0", "PRIMER TIEMPO", seed=166), 1520, 260, w(0.03), rot=2, nombre="m00", entrada="golpe",
          dura=0.1, sonido=SELLO)
    s.clip(1616.0, w(0.1), w(5.04), ancho=ancho, x=X, y=Y, rot=-1, vel=0.6, nombre="clip_cerraba", src=ING1,
           rec=ING1_REC)
    s.pon(etiqueta("INGLATERRA CERRABA", 32, fondo=ROJO), 1520, 520, w(2.36), rot=-1, nombre="cerraba",
          sonido=PAPEL, hasta=w(5.04))
    s.pon(etiqueta("TODOS LOS CAMINOS", 32), 1520, 620, w(3.74), rot=1, nombre="caminos", hasta=w(5.04))
    # Diego con la pelota: corre lento y se congela con los dos ingleses encima
    s.clip(1920.0 - (w(8.04) - w(5.04)) * 0.5, w(5.04), w(8.1), ancho=ancho, x=X, y=Y, rot=1, vel=0.5,
           nombre="clip_dos_ingleses", src=ING1, rec=ING1_REC)
    s.pon(foto(M / "congelados/ing1_diego_dos.png", AL, caja=ING1_REC, seed=167), X, Y, w(8.04), rot=1,
          nombre="congelado_dos_ingleses", entrada="golpe", dura=0.12, sonido=CONGELA)
    for k, (px, py, rw, rh) in enumerate([(680, 400, 150, 230), (450, 470, 160, 200)]):
        cx, cy = en_foto(X, Y, ING1_REC, AL, px, py)
        s.pon(circulo(int(rw * AL / 590), int(rh * AL / 590), seed=30 + k), cx, cy, w(8.1) + k * 0.25,
              nombre=f"circulo_ingles{k + 1}", entrada="trazo", dura=0.3)
    dx, dy = en_foto(X, Y, ING1_REC, AL, 575, 330)
    s.pon(etiqueta("DIEGO", 30), dx, dy - 120, w(5.2), rot=-2, nombre="diego_tira")
    s.pon(etiqueta("DOS INGLESES ENCIMA", 40, fondo=ROJO), 1520, 820, w(8.71), rot=-1.5, nombre="dos_ingleses",
          sonido=PAPEL)
    return s, [(0, 1.0, W / 2, H / 2), (w(8.0), 1.0, W / 2, H / 2), (10.0, 1.1, 760, 560)]


CAPITULO4 = [c4_1, c4_2, c4_3, c4_4, c4_5]


# ═════════════ capítulos 5-9 (18/11): la mano, el gol del siglo, Bélgica, la final, el Mundial de Diego ═════════════
AS = RAIZ / "animaciones/futbol/assets"      # tramos y congelados limpios de las jugadas (cortados con esta misma voz)
FULL = (0, 0, 1920, 1080)
INGF = M / "limpias/inglaterra_fifa.mp4"     # Argentina-Inglaterra sin logos ni marcador
ING = M / "fuentes/inglaterra.mp4"
BEL = M / "fuentes/belgica.mp4"
FIN = M / "fuentes/final.mp4"
FINC = M / "fuentes/final_completo.mp4"
FC_REC = (262, 140, 1658, 1080)              # final completa de FIFA TV: sin columnas, marcador ni logo
REL = RAIZ / ".cache/relatos"                # relatos reales recortados (Víctor Hugo, la llamada con doña Tota)
GOLAZO = {"archivo": "whoosh_grave", "vol": 0.5}


def ancho_de(rec, alto):
    return int(alto * (rec[2] - rec[0]) / (rec[3] - rec[1]))


def jugada(s, pre, tramos, d, X=690, Y=540, AL=700):
    """Una jugada contada sobre papel: tramos de video y cuadros congelados (agrandados, con círculos rojos sobre
    cada jugador y su nombre en tira) uno detrás de otro en el mismo lugar. tramos: ("v", n, t0, dur) o
    ("f", n, t0, dur, [(l, t, w, h, nombre, detalle), ...]) con tiempos de la composición vieja; d = corrimiento."""
    an = ancho_de(FULL, AL)
    for k, tr in enumerate(tramos):
        kind, n, t0, du = tr[:4]
        a, b = t0 + d, t0 + d + du
        if kind == "v":
            s.clip(0.0, a, b + 0.05, ancho=an, x=X, y=Y, vel=1.0, nombre=f"{pre}_tramo{n}", src=AS / f"iv_{pre}_s{n}.mp4",
                   rec=FULL, entrada="corte", dura=0.05)
        else:
            s.pon(foto(AS / f"iv_{pre}_f{n}.png", AL, seed=300 + k), X, Y, max(0, a), nombre=f"{pre}_congelado{n}",
                  entrada="golpe", dura=0.1, sonido=CONGELA, hasta=b + 0.05)
            puestos = []
            for j, (l, t, w_, h_, nm, det) in enumerate(tr[4]):
                cx, cy = en_foto(X, Y, FULL, AL, l + w_ / 2, t + h_ / 2)
                sc = AL / 1080
                arriba, abajo = cy - h_ * sc * 0.55 - 26, cy + h_ * sc * 0.55 + 26
                choca = any(abs(cx - px) < 230 and abs(arriba - py) < 60 for px, py in puestos)
                ty = abajo if choca else arriba
                puestos.append((cx, ty))
                s.pon(etiqueta(nm, 30, fondo=ROJO, seed=j), cx, ty, a + 0.15 + j * 0.25, rot=(-1) ** j * 1.0,
                      nombre=f"tira_{nm.lower()}_{n}", sonido=PAPEL if j == 0 else False, hasta=b + 0.05)
                if det:
                    dy = (abajo + 50) if choca else abajo
                    s.pon(etiqueta(det, 24, seed=j + 3), cx, dy, a + 0.4 + j * 0.25, rot=(-1) ** j * -1.0,
                          nombre=f"detalle_{nm.lower()}_{n}", hasta=b + 0.05)


# ───── capítulo 5: La mano de Dios ─────
VOCES_C5 = ["087b9e41a2e07794", REL / "vh_mano.mp3", "65a22c301ac9979b", "9a219fe79fb89547", "2eea69ac3d3b8ce6"]


def c5_1():
    """Minuto 51: Maradona busca a Valdano; Hodge la tira para atrás; sale Shilton; Diego salta y la empuja con la
    mano izquierda."""
    s = Escena("p6_1", 18.6)
    jugada(s, "mano", [("v", 0, 0, 5.5),
                       ("f", 1, 5.5, 2.9, [(914, 368, 150, 276, "HODGE", "QUIERE DESPEJAR"),
                                           (1152, 383, 135, 216, "MARADONA", None)]),
                       ("v", 2, 8.4, 2.7),
                       ("f", 3, 11.1, 3.7, [(313, 432, 162, 270, "SHILTON", "ARQUERO · 1,83 M"),
                                            (796, 557, 130, 210, "MARADONA", "1,65 M")]),
                       ("v", 4, 14.8, 0.9),
                       ("f", 5, 15.7, 1.9, [(920, 450, 150, 260, "MARADONA", "LA MANO IZQUIERDA"),
                                            (730, 480, 160, 270, "SHILTON", None)]),
                       ("v", 6, 17.6, 1.0)], V - 0.5)
    s.pon(etiqueta("ARGENTINA-INGLATERRA", 30), 1620, 200, w(0.0), rot=-1.5, nombre="partido_mano")
    s.pon(C.sello("51'", tam=76, rot=-6, seed=200), 1620, 400, w(0.57), nombre="minuto51", entrada="golpe",
          dura=0.08, sonido=SELLO)
    s.pon(etiqueta("BUSCA A VALDANO", 28), 1620, 600, w(3.54), rot=1.5, nombre="busca_valdano", hasta=w(7.7))
    s.pon(etiqueta("SE LA TIRA PARA ATRÁS", 28, fondo=ROJO), 1620, 700, w(7.98), rot=-1, nombre="para_atras",
          hasta=w(13.8))
    s.pon(etiqueta("20 CM MÁS ALTO", 30), 1620, 800, w(11.88), rot=1, nombre="veinte_cm", hasta=w(16.3))
    return s, [(0, 1.0, W / 2, H / 2), (18.6, 1.04, 800, 520)]


def c5_2():
    """(Relato original de Víctor Hugo Morales, la mano)."""
    s = Escena("p6_2", 12.9)
    AL = 700
    s.clip(44.4, w(0.0), w(4.0), ancho=ancho_de(FULL, AL), x=700, y=540, vel=1.0, nombre="clip_mano_real", src=INGF,
           rec=FULL)
    s.clip(261.0, w(4.0), w(8.5), ancho=ancho_de(FB_REC, AL), x=700, y=540, vel=0.4, nombre="clip_mano_repeticion",
           src=ING, rec=FB_REC, entrada="corte", dura=0.05)
    s.clip(272.0, w(8.5), 12.9, ancho=ancho_de(FB_REC, AL), x=700, y=540, vel=0.7, nombre="clip_mano_festejo",
           src=ING, rec=FB_REC, entrada="corte", dura=0.05)
    s.pon(foto(M / "victor_hugo.jpg", 300, seed=201), 1620, 330, w(0.2), rot=2, nombre="vh_cara_mano", sonido=PAPEL)
    s.pon(etiqueta("VÍCTOR HUGO MORALES", 30, fondo=ROJO), 1620, 540, w(0.4), rot=-1.5, nombre="vh_nombre_mano")
    s.pon(etiqueta("RELATO ORIGINAL · RADIO", 24), 1620, 630, w(0.6), rot=1, nombre="vh_relato_mano")
    s.pon(diario("«¡Gol!»", 380, 80, resaltar=True, seed=202), 1620, 840, w(2.0), rot=-2, nombre="vh_gol_mano",
          entrada="golpe", dura=0.1, sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (12.9, 1.04, 800, 540)]


def c5_3():
    """Visto desde arriba: Hodge la levanta hacia atrás, Shilton sale con las dos manos y Diego (1,65 m) llega
    primero, con el puño pegado a la cabeza."""
    s = Escena("p6_3", 13.8)
    X, Y, AL, rec = 700, 540, 820, (27, 0, 1099, 823)
    s.pon(foto(M / "eg_mano_shilton.jpg", AL, caja=rec, seed=203), X, Y, w(0.0), rot=-1, nombre="foto_mano_shilton",
          sonido=PAPEL)
    s.pon(etiqueta("ARGENTINA-INGLATERRA · 51'", 28), X, 90, w(0.05), rot=-1, nombre="partido_51")
    s.pon(etiqueta("STEVE HODGE · INGLATERRA", 30), 1530, 300, w(2.72), rot=-1.5, nombre="hodge_levanta", hasta=w(9.1))
    s.pon(etiqueta("SHILTON · DOS MANOS", 30, fondo=ROJO), 1530, 470, w(4.84), rot=1.5, nombre="shilton_dos_manos", hasta=w(10.55))
    s.pon(etiqueta("SHILTON · 1,83 M", 28), 1530, 560, w(5.5), rot=-1, nombre="shilton_183", hasta=w(10.55))
    s.pon(etiqueta("MARADONA · 1,65 M", 28), 1530, 650, w(7.74), rot=1, nombre="diego_165", hasta=w(10.55))
    px, py = en_foto(X, Y, rec, AL, 400, 172)
    s.pon(circulo(230, 200, seed=204), px, py, w(10.63), rot=-1, nombre="circulo_puno", entrada="trazo", dura=0.35)
    s.pon(etiqueta("EL PUÑO", 34, fondo=ROJO), px + 40, py + 160, w(10.8), rot=-2, nombre="el_puno", sonido=PAPEL)
    return s, [(0, 1.0, W / 2, H / 2), (w(10.3), 1.0, W / 2, H / 2), (13.8, 1.3, px + 60, py + 60)]


def c5_4():
    """El árbitro, el tunecino Alí Bin Nasser, no lo ve. Gol. Los ingleses protestan y Diego les grita a sus
    compañeros: vengan a abrazarme, que si no, no lo cobra."""
    s = Escena("p6_4", 12.4)
    X, AL = 700, 680
    s.clip(52.0, w(0.0), w(4.76), ancho=ancho_de(FULL, AL), x=X, y=540, vel=0.6, nombre="clip_no_lo_ve", src=INGF,
           rec=FULL)
    s.pon(etiqueta("ALÍ BIN NASSER", 34, fondo=ROJO), 1560, 230, w(0.84), rot=-1.5, nombre="bin_nasser", sonido=PAPEL,
          hasta=w(6.6))
    s.pon(etiqueta("ÁRBITRO · TÚNEZ", 26), 1560, 320, w(1.2), rot=1, nombre="arbitro_tunez", hasta=w(6.6))
    s.pon(C.sello("NO LO VE", tam=96, rot=-5, seed=205), 1560, 500, w(2.48), nombre="no_lo_ve", entrada="golpe",
          dura=0.08, sonido=SELLO, hasta=w(6.6))
    s.pon(marcador("1 - 0", "MARADONA · 51'", seed=206), 1560, 760, w(3.8), rot=2, nombre="m10_mano", entrada="golpe",
          dura=0.1, sonido=SELLO, hasta=w(6.6))
    s.clip(276.8, w(4.76), w(6.6), ancho=ancho_de(FB_REC, AL), x=X, y=540, vel=0.6, nombre="clip_protestan", src=ING,
           rec=FB_REC, entrada="corte", dura=0.05)
    s.pon(etiqueta("LOS INGLESES PROTESTAN", 30), X, 220, w(5.28), rot=-1, nombre="protestan", hasta=w(6.6))
    s.clip(274.6, w(6.6), 12.4, ancho=ancho_de(FB_REC, AL), x=X, y=540, vel=0.45, nombre="clip_abrazo", src=ING,
           rec=FB_REC, entrada="corte", dura=0.05)
    s.pon(diario("«Vengan a abrazarme,\nque si no,\nno lo cobra»", 620, 52, resaltar=True,
                 arriba="MARADONA, A SUS COMPAÑEROS", seed=207), 1540, 540, w(8.84), rot=1.5, nombre="vengan_abrazarme",
          sonido=PAPEL)
    return s, [(0, 1.0, W / 2, H / 2), (w(8.6), 1.0, W / 2, H / 2), (12.4, 1.05, 1200, 540)]


def c5_5():
    """Esa noche: un poco con la cabeza y otro poco con la mano de Dios. Shilton nunca se lo perdonó: 40 años
    después, todavía no le había dado la mano."""
    s = Escena("p6_5", 14.2)
    fin_a = w(7.2)
    X, Y, AL = 640, 540, 760
    s.pon(foto(M / "mano_dios2.jpg", AL, seed=208), X, Y, w(0.0), rot=1, nombre="foto_mano_dios", sonido=PAPEL,
          hasta=fin_a)
    s.pon(diario("«Un poco con la cabeza\nde Maradona y otro poco\ncon la mano de Dios»", 680, 46, resaltar=True,
                 arriba="MARADONA, ESA NOCHE", seed=209), 1460, 520, w(1.0), rot=-1.5, nombre="cita_mano_dios",
          sonido=PAPEL, hasta=fin_a)
    hx, hy = X + (427 - 1133 / 2) * AL / 823, Y + (172 - 823 / 2) * AL / 823
    s.pon(circulo(200, 190, seed=210), hx, hy, w(5.8), nombre="circulo_mano_dios", entrada="trazo", dura=0.35,
          hasta=fin_a)
    s.pon(foto(M / "shilton.jpg", 560, seed=211), 600, 520, w(7.28), rot=-1.5, nombre="shilton_foto", sonido=PAPEL)
    s.pon(etiqueta("PETER SHILTON", 34, fondo=ROJO), 600, 870, w(7.4), rot=1, nombre="shilton_nombre")
    s.pon(C.sello("NUNCA LO PERDONÓ", tam=80, rot=-5, seed=212), 1400, 380, w(7.99), nombre="nunca_perdono",
          entrada="golpe", dura=0.08, sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (w(7.2), 1.0, W / 2, H / 2), (14.2, 1.05, W / 2, 540)]


CAPITULO5 = [c5_1, c5_2, c5_3, c5_4, c5_5]


# ───── capítulo 6: El gol del siglo ─────
VOCES_C6 = ["193a1d3d754a61e4", "a90c417d89720671", "01d89d547885ccef", REL / "vh_siglo_corto.mp3", "a07247256220d036",
            "5f7679f5af790598", REL / "vh_final.mp3", "09eb805429f4263c", "2f76d1efccf86106"]


def c6_1():
    """Cuatro minutos después, pasó lo otro."""
    s = Escena("p7_1", 3.6)
    s.clip(264.0, 0.0, 3.6, ancho=ancho_de(FULL, 700), x=W / 2, y=600, vel=0.5, nombre="clip_previa_siglo", src=INGF,
           rec=FULL)
    s.pon(C.sello("55'", tam=76, rot=-6, seed=229), 1600, 200, w(0.06), nombre="cuatro_minutos", entrada="golpe",
          dura=0.08, sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (3.6, 1.04, W / 2, 560)]


def c6_2():
    """Minuto 55: Enrique, Maradona en su campo, Beardsley, Reid, Butcher, Fenwick, Shilton... y con Butcher colgado
    de la espalda, gol."""
    s = Escena("p7_2", 23.9)
    jugada(s, "siglo", [("v", 0, 0, 2.5),
                        ("f", 1, 2.5, 2.5, [(1140, 330, 120, 200, "MARADONA", "EN SU PROPIO CAMPO")]),
                        ("v", 2, 5.0, 7.6),
                        ("f", 3, 12.6, 2.3, [(440, 470, 330, 363, "BUTCHER", "AL PISO"),
                                             (980, 450, 187, 363, "MARADONA", None),
                                             (1370, 520, 198, 363, "FENWICK", "LLEGA TARDE")]),
                        ("v", 4, 14.9, 2.5),
                        ("f", 5, 17.4, 2.2, [(310, 360, 132, 209, "SHILTON", "LO DEJA SENTADO"),
                                             (1318, 324, 121, 209, "MARADONA", None)]),
                        ("v", 6, 19.6, 4.4)], V - 0.6)
    s.pon(C.sello("55'", tam=76, rot=-6, seed=213), 1620, 150, w(0.61), nombre="minuto55", entrada="golpe", dura=0.08,
          sonido=SELLO)
    s.pon(etiqueta("ENRIQUE → MARADONA", 26), 1620, 300, w(1.44), rot=1, nombre="enrique_pase")
    for k, (nm, t) in enumerate([("BEARDSLEY", 6.72), ("REID", 7.26), ("BUTCHER", 10.72), ("FENWICK", 12.78),
                                 ("SHILTON", 15.87), ("BUTCHER", 19.17)]):
        s.pon(etiqueta(nm, 30, fondo=ROJO if k % 2 else TINTA, seed=k), 1620, 420 + k * 95, w(t), rot=(-1) ** k * 2,
              nombre=f"dejado_{k + 1}", entrada="golpe", dura=0.08, sonido=PAPEL)
    s.pon(marcador("2 - 0", "MARADONA · 55'", seed=214), 760, 900, w(21.8), rot=-2, nombre="m20_siglo",
          entrada="golpe", dura=0.1, sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (23.9, 1.04, 900, 560)]


def c6_3():
    """Visto desde arriba: en su campo, Beardsley, Reid, la mitad, Butcher, Fenwick, el área, Shilton y Butcher otra
    vez. 60 metros, 10,8 segundos, ni un toque con la derecha."""
    s = Escena("p7_3", 19.8)
    s.pon(foto(M / "diego_festejo_inglaterra.png", 760, seed=219), W / 2, 540, w(0.03), rot=-1.5, nombre="mas_loco", sonido=PAPEL,
          hasta=w(3.1))
    REC6 = (70, 0, 1849, 1080)
    cuadros = [("fifa_266.png", REC6, "EN SU CAMPO", 3.16), ("fifa_270.png", REC6, "BEARDSLEY", 4.46),
               ("fifa_271.png", REC6, "REID", 5.38), ("fifa_274.png", REC6, "BUTCHER", 7.72),
               ("fifa_275.png", REC6, "FENWICK", 8.48), (M / "eludiendo_shilton.jpg", (0, 24, 1140, 716), "SHILTON", 10.33)]
    fin = w(12.5)
    for k, (f, rec, nm, t) in enumerate(cuadros):
        x, y = 360 + (k % 3) * 600, 300 + (k // 3) * 450
        ruta = f if isinstance(f, Path) else COL / f
        s.pon(foto(ruta, 330, caja=rec, seed=220 + k), x, y, w(t), rot=(-1) ** k * 1.5, nombre=f"paso_{k + 1}",
              sonido=PAPEL, hasta=fin)
        s.pon(etiqueta(nm, 28, fondo=ROJO, seed=k), x, y + 200, w(t) + 0.1, rot=(-1) ** k * -1.5,
              nombre=f"paso_{k + 1}_tira", hasta=fin)
    s.pon(etiqueta("Y BUTCHER, OTRA VEZ", 26), 1560, 1010, w(11.42), rot=1, nombre="butcher_otra_vez", hasta=fin)
    s.pon(foto(M / "eg_fenwick.jpg", 760, caja=(141, 0, 805, 900), seed=226), 1450, 540, w(12.5), rot=-1.2,
          nombre="foto_fenwick", sonido=PAPEL)
    s.pon(titulo("60 metros", 104), 600, 250, w(12.5), nombre="sesenta_metros", entrada="golpe", dura=0.1, sonido=SELLO)
    s.pon(titulo("10,8 segundos", 104), 600, 500, w(13.88), nombre="diez_segundos", entrada="golpe", dura=0.1,
          sonido=SELLO)
    s.pon(titulo("0 toques con\nla derecha", 84), 600, 790, w(16.24), nombre="cero_derecha", entrada="golpe", dura=0.1,
          sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (w(12.4), 1.0, W / 2, H / 2), (19.8, 1.05, 800, 520)]


def c6_4():
    """(Relato original de Víctor Hugo Morales del gol del siglo: la jugada entera y las repeticiones)."""
    s = Escena("p7_4", 29.4)
    X, AL = 700, 700
    s.clip(267.5, w(0.0), w(14.0), ancho=ancho_de(FULL, AL), x=X, y=540, vel=1.0, nombre="clip_siglo_entero",
           src=INGF, rec=FULL)
    s.pon(foto(M / "victor_hugo.jpg", 300, seed=227), 1620, 300, w(0.3), rot=2, nombre="vh_cara_siglo", sonido=PAPEL,
          hasta=w(14.0))
    s.pon(etiqueta("VÍCTOR HUGO MORALES", 30, fondo=ROJO), 1620, 510, w(0.5), rot=-1.5, nombre="vh_nombre_siglo",
          hasta=w(14.0))
    s.pon(etiqueta("RELATO ORIGINAL · 22/6/1986", 24), 1620, 600, w(0.7), rot=1, nombre="vh_fecha_siglo", hasta=w(14.0))
    s.pon(diario("«Genio, genio, genio»", 420, 40, resaltar=True, seed=228), 1620, 760, w(7.82), rot=-2,
          nombre="genio", sonido=PAPEL, hasta=w(14.0))
    s.pon(marcador("2 - 0", "MARADONA · 55'", seed=229), 1620, 930, w(11.08), rot=2, nombre="m20_relato",
          entrada="golpe", dura=0.1, sonido=SELLO, hasta=w(14.0))
    reps = [(302.0, 0.6, 14.0, 17.5), (310.0, 0.8, 17.5, 21.0), (318.0, 0.5, 21.0, 24.5)]   # las 3 repeticiones
    for k, (desde, vel, a, b) in enumerate(reps):
        s.clip(desde, w(a), w(b), ancho=ancho_de(FB_REC, AL), x=X + (-1) ** k * 30, y=540, vel=vel, rot=(-1) ** k * 1.5,
               nombre=f"repeticion_{k + 1}", src=ING, rec=FB_REC)
    s.pon(etiqueta("LA REPETICIÓN", 30), 1620, 300, w(14.2), rot=-1.5, nombre="repeticion_tira", hasta=w(24.5))
    s.pon(foto(M / "eludiendo_shilton.jpg", 820, seed=230), W / 2, 540, w(24.5), rot=-0.8, nombre="foto_eludiendo",
          sonido=PAPEL)
    s.pon(C.sello("EL GOL DEL SIGLO", tam=90, rot=-5, seed=231), 1350, 940, w(25.3), nombre="sello_gol_siglo",
          entrada="golpe", dura=0.08, sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (w(24.5), 1.0, W / 2, H / 2), (29.4, 1.06, W / 2, 520)]


def c6_5():
    """Eso que escuchaste es Víctor Hugo Morales: barrilete cósmico, ¿de qué planeta viniste? Y Lineker confesó que
    fue la única vez que tuvo ganas de aplaudir un gol del rival."""
    s = Escena("p7_5", 15.8)
    fin_a = w(7.5)
    s.pon(foto(M / "victor_hugo.jpg", 560, seed=232), 540, 500, w(0.0), rot=-1.5, nombre="vh_cara", sonido=PAPEL,
          hasta=fin_a)
    s.pon(etiqueta("VÍCTOR HUGO MORALES · EN LA RADIO", 28, fondo=ROJO), 540, 860, w(1.33), rot=1, nombre="vh_radio",
          hasta=fin_a)
    s.pon(diario("«Barrilete cósmico,\n¿de qué planeta\nviniste?»", 640, 58, resaltar=True, seed=233), 1380, 520,
          w(3.98), rot=1.5, nombre="barrilete", entrada="golpe", dura=0.12, sonido=SELLO, hasta=fin_a)
    s.clip(270.0, w(7.56), 15.8, ancho=ancho_de(FULL, 640), x=640, y=540, vel=0.3, nombre="clip_siglo_lento", src=INGF,
           rec=FULL)
    s.pon(etiqueta("GARY LINEKER", 36, fondo=ROJO), 1500, 260, w(7.6), rot=-1.5, nombre="lineker", sonido=PAPEL)
    s.pon(etiqueta("DELANTERO DE INGLATERRA", 26), 1500, 360, w(8.23), rot=1, nombre="lineker_delantero")
    s.pon(diario("«Tuve ganas\nde aplaudir»", 560, 60, resaltar=True, arriba="LINEKER, SOBRE EL GOL DE DIEGO",
                 seed=234), 1500, 640, w(12.41), rot=-1.5, nombre="ganas_de_aplaudir", sonido=PAPEL)
    return s, [(0, 1.0, W / 2, H / 2), (w(7.5), 1.0, W / 2, H / 2), (15.8, 1.04, 1000, 540)]


def c6_6():
    """2002, votación de la FIFA: el gol del siglo. El más sucio y el mejor de todos los tiempos, el mismo día, con
    cuatro minutos de diferencia. Cuarenta años después, todavía no nos cansamos de verlo."""
    s = Escena("p7_6", 18.0)
    fin_a = w(5.3)
    s.pon(foto(M / "eludiendo_shilton.jpg", 740, seed=235), 680, 540, w(0.0), rot=-1, nombre="eludiendo_2002",
          sonido=PAPEL, hasta=fin_a)
    s.pon(etiqueta("VOTACIÓN DE LA FIFA · 2002", 30), 1520, 300, w(0.12), rot=-1.5, nombre="votacion_fifa", hasta=fin_a)
    s.pon(C.sello("GOL DEL SIGLO", tam=90, rot=-5, seed=234), 1520, 560, w(3.7), nombre="gol_del_siglo",
          entrada="golpe", dura=0.08, sonido=SELLO, hasta=fin_a)
    fin_b = w(12.4)
    s.pon(foto(M / "mano_dios2.jpg", 440, seed=236), 540, 430, w(5.38), rot=-2, nombre="dos_goles_mano", sonido=PAPEL,
          hasta=fin_b)
    s.pon(etiqueta("EL MÁS SUCIO", 34, fondo=ROJO), 540, 720, w(5.52), rot=1.5, nombre="el_mas_sucio", hasta=fin_b)
    s.pon(foto(M / "eludiendo_shilton.jpg", 440, seed=237), 1380, 430, w(6.07), rot=2, nombre="dos_goles_siglo",
          sonido=PAPEL, hasta=fin_b)
    s.pon(etiqueta("EL MEJOR", 34), 1380, 720, w(6.25), rot=-1.5, nombre="el_mejor", hasta=fin_b)
    s.pon(etiqueta("51'", 40), 540, 150, w(9.7), rot=-2, nombre="minuto_51_b", hasta=fin_b)
    s.pon(etiqueta("55'", 40), 1380, 150, w(9.7) + 0.2, rot=2, nombre="minuto_55_b", hasta=fin_b)
    s.clip(270.0, w(12.42), 18.0, ancho=ancho_de(FULL, 760), x=W / 2, y=560, vel=0.3, nombre="clip_siglo_otra_vez",
           src=INGF, rec=FULL)
    s.pon(etiqueta("40 AÑOS DESPUÉS", 30, fondo=ROJO), W / 2, 110, w(12.98), rot=-1, nombre="cuarenta_despues")
    return s, [(0, 1.0, W / 2, H / 2), (w(12.4), 1.0, W / 2, H / 2), (18.0, 1.05, W / 2, 560)]


def c6_7():
    """(Víctor Hugo: «Gracias, Dios, por el fútbol, por Maradona, por estas lágrimas»)."""
    s = Escena("p7_7", 7.4)
    s.clip(305.0, w(0.0), 7.4, ancho=ancho_de(FB_REC, 700), x=720, y=540, vel=0.4, nombre="clip_lagrimas", src=ING,
           rec=FB_REC)
    s.pon(diario("«Gracias, Dios,\npor el fútbol,\npor Maradona,\npor estas lágrimas»", 560, 50, resaltar=True,
                 arriba="VÍCTOR HUGO MORALES", seed=238), 1560, 540, w(0.1), rot=1.5, nombre="gracias_dios", sonido=PAPEL)
    return s, [(0, 1.0, W / 2, H / 2), (7.4, 1.04, 900, 540)]


def c6_8():
    """Lineker descontó a los 81. Pero ya era tarde: Argentina 2, Inglaterra 1. A semifinales."""
    s = Escena("p7_8", 8.6)
    s.pon(foto(M / "eg_festejo_yako.jpg", 760, caja=(227, 0, 710, 588), seed=239), 1450, 520, w(0.3), rot=1.4,
          nombre="festejo_yako", sonido=PAPEL)
    s.pon(etiqueta("FOTO: DANI YAKO", 20), 1450, 960, w(0.5), rot=-1, nombre="credito_yako")
    s.pon(etiqueta("CUARTOS DE FINAL · AZTECA", 28), 580, 140, w(0.04), rot=-1.5, nombre="cuartos_azteca")
    s.pon(etiqueta("LINEKER 81'", 34, fondo=ROJO), 580, 280, w(0.04), rot=1.5, nombre="lineker_81", sonido=PAPEL)
    s.pon(marcador("2 - 1", "ARGENTINA · INGLATERRA", seed=240), 580, 640, w(3.41), rot=-2, nombre="m21",
          entrada="golpe", dura=0.1, sonido=SELLO)
    s.pon(C.sello("A SEMIFINALES", tam=88, rot=-5, seed=241), 580, 900, w(6.18), nombre="a_semis", entrada="golpe",
          dura=0.08, sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (8.6, 1.04, 1000, 540)]


def c6_9():
    """Y todavía faltaba una final. Si te gustan estas historias, suscribite a LOS 11."""
    s = Escena("p7_9", 10.2)
    s.pon(foto(M / "eg_telefono.jpg", 700, caja=(65, 0, 462, 486), seed=242), 1450, 540, w(0.03), rot=-1.2,
          nombre="telefono_diego", sonido=PAPEL)
    s.pon(etiqueta("MÉXICO, 1986", 22), 1450, 930, w(2.6), rot=1, nombre="mexico_86_tel")
    s.pon(titulo("Suscribite\na LOS 11", 118), 620, 420, w(3.76), nombre="suscribite_mitad", entrada="golpe", dura=0.1,
          sonido=SELLO)
    s.pon(etiqueta("TODO EL FÚTBOL, COMO MERECE SER CONTADO", 26, fondo=ROJO), 620, 720, w(5.66), rot=-1,
          nombre="como_merece")
    return s, [(0, 1.0, W / 2, H / 2), (10.2, 1.04, 800, 520)]


CAPITULO6 = [c6_1, c6_2, c6_3, c6_4, c6_5, c6_6, c6_7, c6_8, c6_9]


# ───── capítulo 7: Bélgica ─────
VOCES_C7 = ["2ca231228ecad566", "c3ac3716488e58f4", "9d438a45a65168ba"]


def c7_1():
    """Semifinal, Bélgica: la sorpresa, que eliminó a la URSS y a España. Minuto 51: entre dos defensores, la pica
    por encima del arquero."""
    s = Escena("p8_1", 15.0)
    X, AL = 700, 680
    fin_a = w(6.96)
    s.clip(20.0, w(0.0), fin_a, ancho=ancho_de(FB_REC, AL), x=X, y=540, vel=0.5, nombre="clip_salida_belgica", src=BEL,
           rec=FB_REC)
    s.pon(etiqueta("SEMIFINAL · AZTECA · 25 DE JUNIO", 26), 1560, 200, w(0.14), rot=-1.5, nombre="semi_fecha",
          hasta=fin_a)
    s.pon(marcador("ARG  vs  BÉL", "SEMIFINAL", seed=243), 1560, 400, w(1.13), rot=2, nombre="vs_belgica",
          entrada="golpe", dura=0.1, sonido=SELLO, hasta=w(2.25))
    s.pon(foto(BAN / "belgium.png", 200, seed=242), 1560, 640, w(2.32), rot=3, nombre="sorpresa", sonido=PAPEL,
          hasta=fin_a)
    s.pon(etiqueta("ELIMINÓ A LA URSS", 28, fondo=ROJO), 1560, 830, w(4.92), rot=1, nombre="elimino_urss", hasta=fin_a)
    s.pon(etiqueta("Y A ESPAÑA", 28, fondo=ROJO), 1560, 920, w(5.9), rot=-1, nombre="elimino_espana", hasta=fin_a)
    vel = 0.8
    s.clip(270.0 - (w(12.04) - fin_a) * vel, fin_a, 15.0, ancho=ancho_de(FB_REC, AL), x=X, y=540, vel=vel,
           nombre="clip_gol_belgica_1", src=BEL, rec=FB_REC, entrada="corte", dura=0.05)
    s.pon(C.sello("51'", tam=76, rot=-6, seed=244), 1560, 560, w(9.33), nombre="minuto51_bel", entrada="golpe",
          dura=0.08, sonido=SELLO, hasta=w(12.5))
    s.pon(marcador("1 - 0", "MARADONA · 51'", seed=245), 1560, 820, w(12.6), rot=-2, nombre="m10_bel",
          entrada="golpe", dura=0.1, sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (15.0, 1.04, 900, 540)]


def c7_2():
    """Minuto 63: desde la izquierda, pegado a la raya; un belga en el piso, otro pasado de largo; sale Pfaff y
    Diego la cruza. Otra vez."""
    s = Escena("p8_2", 12.8)
    jugada(s, "belg2", [("v", 0, 0, 4.2),
                        ("f", 1, 4.2, 3.0, [(1290, 285, 120, 230, "MARADONA", None),
                                            (1330, 125, 220, 150, "BÉLGICA", "EN EL PISO"),
                                            (165, 200, 150, 200, "PFAFF", "ARQUERO")]),
                        ("v", 2, 7.2, 3.3)], V - 0.4)
    s.clip(362.0, 10.5 + V - 0.4, 12.8, ancho=ancho_de(FB_REC, 700), x=690, y=540, vel=0.4, nombre="clip_festejo_bel",
           src=BEL, rec=FB_REC, entrada="corte", dura=0.05)
    s.pon(C.sello("63'", tam=76, rot=-6, seed=246), 1620, 200, w(0.52), nombre="minuto63", entrada="golpe", dura=0.08,
          sonido=SELLO)
    s.pon(etiqueta("PEGADO A LA RAYA", 28), 1620, 400, w(2.93), rot=1, nombre="pegado_raya", hasta=w(7.6))
    s.pon(marcador("2 - 0", "MARADONA · 63'", seed=247), 1620, 820, w(10.15), rot=2, nombre="m20_bel",
          entrada="golpe", dura=0.1, sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (12.8, 1.04, 900, 540)]


def c7_3():
    """Dos a cero, a la final. Invicta: cinco victorias y un empate. Y un solo nombre en todos los diarios."""
    s = Escena("p8_3", 10.4)
    s.pon(etiqueta("ARGENTINA, A LA FINAL", 34, fondo=ROJO), 560, 120, w(0.0), rot=-1.5, nombre="a_la_final",
          sonido=PAPEL)
    s.pon(C.sello("INVICTA", tam=110, rot=-5, seed=248), 560, 250, w(2.86), nombre="invicta", entrada="golpe",
          dura=0.08, sonido=SELLO)
    for k, r in enumerate(["COREA 3-1", "ITALIA 1-1", "BULGARIA 2-0", "URUGUAY 1-0", "INGLATERRA 2-1",
                           "BÉLGICA 2-0"]):
        s.pon(etiqueta(r, 30, fondo=ROJO if k == 1 else TINTA, seed=k), 560, 390 + k * 85, w(3.0) + k * 0.15,
              rot=(-1) ** k * 1.2, nombre=f"resultado_{k + 1}", dura=0.2, sonido=PAPEL if k % 2 == 0 else False)
    s.pon(etiqueta("5 VICTORIAS · 1 EMPATE", 34), 560, 930, w(3.94), rot=-1, nombre="cinco_y_uno")
    s.pon(foto(M / "eg_tapa_3481.jpg", 880, seed=248), 1430, 540, w(6.1), rot=1.5, nombre="tapa_no_llores",
          entrada="golpe", dura=0.12, sonido=PAPEL)
    s.pon(etiqueta("EL GRÁFICO · 24/6/1986", 22), 1430, 1010, w(6.4), rot=-1, nombre="credito_tapa_3481")
    return s, [(0, 1.0, W / 2, H / 2), (w(6.0), 1.0, W / 2, H / 2), (10.4, 1.07, 1300, 520)]


CAPITULO7 = [c7_1, c7_2, c7_3]


# ───── capítulo 8: La final ─────
VOCES_C8 = ["120b395474da3edb", "dff0c7de009b44f8", "2b7486b65e8c4f8d", "655f6bfe5560649f", "5e08ed8ae10930f0",
            "880d6a608ef838e3", "c3736885dd92dbcb", "bb4adba8b098588c", "5df19b3ff72d8d17", None]


def c8_1():
    """29 de junio, el Azteca otra vez lleno. Alemania Federal de Beckenbauer, que eliminó a la Francia de Platini.
    Rummenigge, Völler, Schumacher... y Matthäus, con una misión: perseguir a Maradona."""
    s = Escena("p9_1", 21.0)
    fin_a = w(3.9)
    s.clip(44.5, w(0.0), fin_a, ancho=ancho_de(FB_REC, 700), x=720, y=540, vel=0.5, nombre="clip_azteca_final",
           src=FIN, rec=FB_REC)
    s.pon(etiqueta("29 DE JUNIO DE 1986", 40, fondo=ROJO), 1580, 260, w(0.03), rot=-1.5, nombre="veintinueve",
          entrada="golpe", dura=0.1, sonido=PAPEL, hasta=fin_a)
    s.pon(etiqueta("LA FINAL · ESTADIO AZTECA", 28), 1580, 380, w(1.64), rot=1, nombre="final_azteca", hasta=fin_a)
    fin_b = w(11.1)
    s.pon(etiqueta("ALEMANIA FEDERAL", 40, fondo=ROJO), 520, 150, w(4.67), rot=-1.5, nombre="alemania", sonido=PAPEL,
          hasta=fin_b)
    s.pon(foto(M / "beckenbauer_dt.jpg", 480, seed=249), 520, 520, w(6.0), rot=-1.5, nombre="beckenbauer", sonido=PAPEL,
          hasta=fin_b)
    s.pon(etiqueta("FRANZ BECKENBAUER · DT", 28), 520, 850, w(7.02), rot=1, nombre="beckenbauer_dt", hasta=fin_b)
    s.pon(foto(BAN / "france.png", 260, seed=250), 1400, 500, w(8.37), rot=3, nombre="platini", sonido=PAPEL,
          hasta=fin_b)
    s.pon(C.sello("ELIMINADA", tam=80, rot=-8, seed=251), 1400, 520, w(8.9), nombre="francia_eliminada",
          entrada="golpe", dura=0.08, sonido=SELLO, hasta=fin_b)
    fin_c = w(14.0)
    for k, (n, nm, t) in enumerate([("rummenigge86.jpg", "RUMMENIGGE", 11.19), ("voller_figurita.jpg", "VÖLLER", 12.3),
                                    ("schumacher86.jpg", "SCHUMACHER", 13.42)]):
        x = 420 + k * 540
        s.pon(foto(M / n, 400, seed=250 + k), x, 470, w(t), rot=(-1) ** k * 2, nombre=f"aleman_{nm.lower()}",
              sonido=PAPEL, hasta=fin_c)
        s.pon(etiqueta(nm, 32, seed=k), x, 720, w(t), rot=(-1) ** k * -1.5, nombre=f"aleman_{nm.lower()}_tira",
              hasta=fin_c)
    # Matthäus al lado de Diego, en la final: la foto ya dice "perseguirlo"
    s.pon(foto(M / "matthaus_diego.jpg", 620, seed=253), W / 2, 500, w(14.03), rot=-1.5, nombre="matthaus", sonido=PAPEL)
    s.pon(etiqueta("LOTHAR MATTHÄUS", 34, fondo=ROJO), 660, 880, w(14.54), rot=1, nombre="matthaus_nombre")
    s.pon(etiqueta("DIEGO", 34), 1220, 880, w(17.83), rot=-1.5, nombre="diego_perseguido", sonido=PAPEL)
    return s, [(0, 1.0, W / 2, H / 2), (w(14.0), 1.0, W / 2, H / 2), (21.0, 1.05, 1000, 560)]


def cancha(ancho=1780, alto=940, seed=7):
    """Cancha vista desde arriba (pasto a franjas y líneas de cal), recortada a tijera: para presentar alineaciones
    (18/11, nota del usuario: "siempre que presenten alineación hacé una cancha"). Ataca hacia la derecha."""
    rng = np.random.default_rng(seed)
    xs = np.arange(ancho)
    franja = ((xs // (ancho / 14)).astype(int) % 2)[None, :, None]
    base = np.array([62, 122, 58]) + franja * np.array([10, 16, 8])
    a = np.broadcast_to(base, (alto, ancho, 3)).astype("float32") + rng.normal(0, 5, (alto, ancho, 1))
    im = Image.fromarray(np.clip(a, 0, 255).astype("uint8"))
    d = ImageDraw.Draw(im)
    L, g = (238, 236, 224), 6
    m = 34
    x0, y0, x1, y1 = m, m, ancho - m, alto - m
    cx, cy = ancho / 2, alto / 2
    d.rectangle([x0, y0, x1, y1], outline=L, width=g)
    d.line([(cx, y0), (cx, y1)], fill=L, width=g)
    r = alto * 0.13
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=L, width=g)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=L)
    ah, aw = alto * 0.58, ancho * 0.145            # área grande
    ch, cw = alto * 0.26, ancho * 0.05             # área chica
    for lado in (0, 1):
        xa = x0 if lado == 0 else x1
        sg = 1 if lado == 0 else -1
        d.rectangle(sorted([xa, xa + sg * aw])[:1] + [cy - ah / 2] + sorted([xa, xa + sg * aw])[1:] + [cy + ah / 2],
                    outline=L, width=g)
        d.rectangle(sorted([xa, xa + sg * cw])[:1] + [cy - ch / 2] + sorted([xa, xa + sg * cw])[1:] + [cy + ch / 2],
                    outline=L, width=g)
        px = xa + sg * ancho * 0.1
        d.ellipse([px - 6, cy - 6, px + 6, cy + 6], fill=L)
        rr = alto * 0.13
        bb = [px - rr, cy - rr, px + rr, cy + rr]
        d.arc(bb, -53 if lado == 0 else 127, 53 if lado == 0 else 233, fill=L, width=g)
        d.rectangle(sorted([xa, xa - sg * 16])[:1] + [cy - alto * 0.06] + sorted([xa, xa - sg * 16])[1:] +
                    [cy + alto * 0.06], fill=L)                   # arco
    return C.recorte_cuadro(im, seed=seed)


def c8_2():
    """Bilardo salió con los de siempre: Pumpido; Cuciuffo, Brown, Ruggeri; Giusti, Batista, Enrique,
    Olarticoechea; Burruchaga, Valdano y Diego."""
    s = Escena("p9_2", 15.0)
    s.pon(cancha(), W / 2, 565, w(0.0), rot=-0.4, nombre="cancha_final", sonido=PAPEL)
    s.pon(etiqueta("LA FINAL · 3-5-2 · LOS DE SIEMPRE", 28), W / 2, 60, w(0.03), rot=-1, nombre="formacion_final")
    equipo = [("pumpido", 220, 540, 2.04), ("cuciuffo", 580, 260, 3.57), ("brown", 580, 540, 4.47),
              ("ruggeri", 580, 820, 5.01), ("giusti", 960, 190, 7.0), ("batista", 960, 430, 7.71),
              ("enrique", 960, 670, 8.41), ("olarticoechea", 960, 910, 9.02), ("burruchaga", 1340, 380, 11.08),
              ("valdano", 1340, 700, 12.25), ("maradona", 1620, 540, 13.0)]
    for k, (n, x, y, t) in enumerate(equipo):
        al = 230 if n == "maradona" else 170
        s.pon(cara(n, al, seed=260 + k), x, y, w(t), rot=(-1) ** k * 2, nombre=f"titular_{n}", dura=0.35,
              sonido=PAPEL)
        s.pon(etiqueta(n.upper() if n != "maradona" else "DIEGO", 22 if n != "maradona" else 30,
                       fondo=ROJO if n == "maradona" else TINTA, seed=k), x, y + al / 2 + 30, w(t) + 0.1,
              rot=(-1) ** k * -1.5, nombre=f"titular_{n}_tira", dura=0.35)
    return s, [(0, 1.0, W / 2, H / 2), (w(12.9), 1.0, W / 2, H / 2), (15.0, 1.04, 1150, 545)]


def c8_3():
    """Minuto 23: tiro libre de Burruchaga, Schumacher sale y se queda; José Luis Brown, que nunca había hecho un gol
    con la selección, la cabecea al arco vacío. Uno a cero. (18/11, nota del usuario: "que se vea el gol, intervenido,
    y no hace falta que TODO lo que dice el locutor esté en texto, mejor en imágenes".)"""
    s = Escena("p9_3", 16.8)
    FREC = (300, 150, 1920, 960)                   # Football Flashback sin logo, marcador ni url, CON el arco
    X, Y, AL = W / 2, 545, 849
    an = ancho_de(FREC, AL)
    s.pon(marcador("0 - 0", "ARG · ALE · 23'", seed=270), X, Y, w(0.0), nombre="m00_final", sonido=False,
          hasta=w(14.55))
    s.clip(116.4, w(0.0), w(5.2), ancho=an, x=X, y=Y, vel=0.55, nombre="clip_tiro_libre", src=FIN, rec=FREC)
    s.pon(etiqueta("TIRO LIBRE · BURRUCHAGA", 30, fondo=ROJO), X, 1030, w(1.05), nombre="tiro_libre", hasta=w(5.2))
    s.clip(119.55, w(5.2), w(6.75), ancho=an, x=X, y=Y, vel=0.3, nombre="clip_sale_schumacher", src=FIN, rec=FREC,
           entrada="corte", dura=0.05)
    s.pon(foto(M / "congelados/fin_brown_sale.png", AL, caja=FREC, seed=271), X, Y, w(6.7), nombre="congelado_sale",
          entrada="golpe", dura=0.1, sonido=CONGELA, hasta=w(8.45))
    kx, ky = en_foto(X, Y, FREC, AL, 1130, 285)
    s.pon(etiqueta("SCHUMACHER", 30, fondo=ROJO), kx, ky - 95, w(6.85), nombre="tira_schumacher", sonido=PAPEL,
          hasta=w(8.45))
    s.pon(etiqueta("SALE... Y SE QUEDA", 24), kx, ky + 110, w(7.16), nombre="se_queda", hasta=w(8.45))
    s.clip(120.0, w(8.4), w(10.45), ancho=an, x=X, y=Y, vel=0.3, nombre="clip_cabezazo", src=FIN, rec=FREC,
           entrada="corte", dura=0.05)
    s.pon(foto(M / "congelados/fin_brown_cabeza.png", AL, caja=FREC, seed=272), X, Y, w(10.4), nombre="congelado_cabeza",
          entrada="golpe", dura=0.1, sonido=CONGELA, hasta=w(13.0))
    bx, by = en_foto(X, Y, FREC, AL, 915, 235)
    s.pon(etiqueta("BROWN", 32, fondo=ROJO), bx, by - 80, w(10.5), nombre="tira_brown", sonido=PAPEL, hasta=w(13.0))
    s.pon(foto(M / "eg_brown.jpg", 260, seed=273), 1640, 300, w(10.7), rot=2, nombre="brown_cara", hasta=w(13.0))
    s.pon(etiqueta("SU PRIMER GOL CON LA SELECCIÓN", 24), 1640, 450, w(10.9), rot=-1, nombre="primer_gol",
          hasta=w(13.0))
    im, cx, cy = trayecto([en_foto(X, Y, FREC, AL, *p) for p in ((960, 225), (1300, 260), (1640, 410))])
    s.pon(im, cx, cy, w(11.3), nombre="pelota_al_arco", entrada="trazo", dura=0.6, hasta=w(13.0))
    s.clip(120.6, w(13.0), w(14.4), ancho=an, x=X, y=Y, vel=0.6, nombre="clip_gol_brown", src=FIN, rec=FREC,
           entrada="corte", dura=0.05)
    s.clip(121.5, w(14.4), 16.8, ancho=an, x=X, y=Y, vel=0.7, nombre="clip_festejo_brown", src=FIN, rec=FREC,
           entrada="corte", dura=0.05)
    s.pon(marcador("1 - 0", "BROWN 23'", seed=274), X, Y, w(14.55), nombre="m10_final", sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (16.8, 1.03, W / 2, 545)]


def c8_4():
    """Brown se dislocó el hombro: le hizo un agujero a la camiseta, metió el dedo para sostener el brazo y siguió
    jugando. No quería salir de una final del mundo."""
    s = Escena("p9_4", 13.2)
    s.pon(foto(M / "brown.jpg", 700, seed=274), 520, 540, w(0.0), rot=-1.5, nombre="brown_foto", sonido=PAPEL,
          hasta=w(3.6))
    s.pon(etiqueta("HOMBRO DISLOCADO", 36, fondo=ROJO), 1350, 400, w(1.74), rot=-1.5, nombre="hombro", sonido=PAPEL,
          hasta=w(3.6))
    s.pon(foto(M / "brown_camiseta.jpg", 780, seed=275), 560, 540, w(3.6), rot=1, nombre="brown_camiseta",
          sonido=PAPEL)
    s.pon(etiqueta("UN AGUJERO EN LA CAMISETA", 30), 1400, 260, w(3.66), rot=-1.5, nombre="agujero")
    s.pon(etiqueta("EL DEDO SOSTIENE EL BRAZO", 30, fondo=ROJO), 1400, 380, w(5.77), rot=1, nombre="el_dedo")
    s.pon(C.sello("SIGUIÓ JUGANDO", tam=88, rot=-5, seed=276), 1400, 580, w(7.72), nombre="siguio_jugando",
          entrada="golpe", dura=0.08, sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (13.2, 1.05, 700, 520)]


def c8_5():
    """Minuto 55: Enrique para Valdano, que entra solo y la cruza. Dos a cero. Parecía terminado."""
    s = Escena("p9_5", 8.6)
    X, AL = 720, 700
    s.clip(285.0 - (w(4.6) - w(0.0)), w(0.0), w(5.9), ancho=ancho_de(FB_REC, AL), x=X, y=540, vel=1.0,
           nombre="clip_gol_valdano", src=FIN, rec=FB_REC)
    s.clip(287.0, w(5.9), 8.6, ancho=ancho_de(FB_REC, AL), x=X, y=540, vel=0.4, nombre="clip_festejo_valdano", src=FIN,
           rec=FB_REC, entrada="corte", dura=0.05)
    s.pon(C.sello("55'", tam=76, rot=-6, seed=277), 1620, 200, w(0.63), nombre="minuto55_final", entrada="golpe",
          dura=0.08, sonido=SELLO)
    s.pon(etiqueta("ENRIQUE PARA VALDANO", 28), 1620, 380, w(1.66), rot=1, nombre="enrique_valdano")
    s.pon(marcador("2 - 0", "VALDANO · 55'", seed=278), 1620, 620, w(5.3), rot=2, nombre="m20_final", entrada="golpe",
          dura=0.1, sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (8.6, 1.04, 900, 540)]


def c8_6():
    """Alemania no se rendía: dos córners, dos goles. 74': Rummenigge. 80': Völler. Dos a dos. El Azteca, en
    silencio."""
    s = Escena("p9_6", 14.4)
    X, AL = 720, 700
    s.pon(foto(BAN / "germany.png", 420, seed=279), W / 2, 500, w(0.06), rot=-2, nombre="no_se_rendia",
          sonido=PAPEL, hasta=w(2.7))
    s.pon(etiqueta("DOS CÓRNERS, DOS GOLES", 30, fondo=ROJO), W / 2, 1035, w(2.7), rot=-1, nombre="dos_corners",
          sonido=PAPEL, hasta=w(10.9))
    goles_juntos(s, [dict(desde=374.5 - (w(5.98) - w(2.7)), t=w(2.7), src=FIN, rec=FB_REC, vel=1.0,
                          nombre="clip_gol_rummenigge", texto="ARG 2-1 ALE", sub="RUMMENIGGE 74'", t_marca=w(5.98)),
                     dict(desde=451.0 - (w(8.38) - w(7.6)), t=w(7.6), src=FIN, rec=FB_REC, vel=1.0,
                          nombre="clip_gol_voller", texto="ARG 2-2 ALE", sub="VÖLLER 80'", t_marca=w(9.72))],
                 hasta=w(10.9))
    s.clip(376.5, w(10.9), 14.4, ancho=ancho_de(FB_REC, AL), x=X, y=540, vel=0.4, nombre="clip_silencio", src=FIN,
           rec=FB_REC, entrada="corte", dura=0.05)
    s.pon(marcador("2 - 2", "ARG · ALE", seed=280), 1620, 520, w(10.9), rot=-2, nombre="m22_final", sonido=False)
    return s, [(0, 1.0, W / 2, H / 2), (14.4, 1.04, 900, 540)]


def c8_7():
    """Minuto 84: Maradona, rodeado de alemanes, levanta la cabeza y mete el pase; Burruchaga corre con Briegel atrás
    y la cruza ante Schumacher. Tres a dos."""
    s = Escena("p9_7", 14.3)
    jugada(s, "burru", [("v", 0, 0, 2.8),
                        ("f", 1, 2.8, 3.6, [(751, 497, 330, 418, "MARADONA", "RODEADO DE ALEMANES")]),
                        ("v", 2, 6.4, 2.4),
                        ("f", 3, 8.8, 2.6, [(960, 306, 144, 252, "BURRUCHAGA", "SOLO HACIA EL ARCO"),
                                            (978, 540, 156, 240, "BRIEGEL", "LO PERSIGUE")]),
                        ("v", 4, 11.4, 1.2),
                        ("f", 5, 12.6, 1.0, [(770, 477, 368, 172, "SCHUMACHER", None)]),
                        ("v", 6, 13.6, 1.2)], V - 1.0)
    s.pon(C.sello("84'", tam=76, rot=-6, seed=281), 1620, 200, w(0.6), nombre="minuto84", entrada="golpe", dura=0.08,
          sonido=SELLO)
    s.pon(etiqueta("EL PASE", 34, fondo=ROJO), 1620, 420, w(5.68), rot=1.5, nombre="el_pase")
    s.pon(marcador("3 - 2", "BURRUCHAGA · 84'", seed=282), 1620, 880, w(12.42), rot=2, nombre="m32",
          entrada="golpe", dura=0.1, sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (14.3, 1.04, 900, 540)]


def c8_8():
    """Mirá el pase: tres alemanes encima, levanta la cabeza una vez, 40 metros con un toque. Briegel no llega. El
    mejor del mundo, en el 84 de una final, hizo lo más simple."""
    s = Escena("p9_8", 20.8)
    fin_a = w(13.4)
    s.pon(etiqueta("ARGENTINA-ALEMANIA · 84'", 28), W / 2, 60, w(0.04), rot=-1, nombre="partido_84", hasta=fin_a)
    s.pon(foto(COL / "fin_465.5.png", 380, caja=(109, 150, 1810, 960), seed=283), 540, 320, w(0.04), rot=0.9,
          nombre="pase_1", sonido=PAPEL, hasta=fin_a)
    s.pon(etiqueta("3 ALEMANES ENCIMA", 28, fondo=ROJO), 540, 550, w(1.75), rot=-1, nombre="tres_alemanes", hasta=fin_a)
    s.pon(foto(COL / "fin_467.png", 380, caja=(150, 150, 1770, 960), seed=284), 1400, 320, w(4.24), rot=-0.6,
          nombre="pase_2", sonido=PAPEL, hasta=fin_a)
    s.pon(etiqueta("LEVANTA LA CABEZA · UNA VEZ", 26), 1400, 550, w(4.4), rot=1, nombre="levanta_cabeza", hasta=fin_a)
    s.pon(foto(COL / "fin_469.png", 380, caja=(109, 150, 1810, 960), seed=285), 540, 760, w(6.53), rot=1.4,
          nombre="pase_3", sonido=PAPEL, hasta=fin_a)
    s.pon(etiqueta("40 METROS · UN TOQUE", 28), 540, 990, w(8.4), rot=-1, nombre="cuarenta_metros", hasta=fin_a)
    s.pon(etiqueta("BRIEGEL NO LLEGA", 30, fondo=ROJO), 1400, 760, w(10.87), rot=1.5, nombre="briegel_no_llega",
          sonido=PAPEL, hasta=fin_a)
    s.pon(foto(M / "diego_final_salto.jpg", 520, seed=286), 560, 520, w(13.48), rot=-2, nombre="diego_simple", sonido=PAPEL)
    s.pon(etiqueta("MINUTO 84 · FINAL DEL MUNDO", 28, fondo=ROJO), 560, 880, w(15.4), rot=1, nombre="minuto84_final")
    return s, [(0, 1.0, W / 2, H / 2), (w(13.4), 1.0, W / 2, H / 2), (20.8, 1.06, 1000, 520)]


def c8_9():
    """Seis minutos después, Romualdo Arppi Filho termina el partido. Argentina es campeón del mundo."""
    s = Escena("p9_9", 9.2)
    X, AL = 700, 680
    s.clip(482.0, w(0.0), w(5.8), ancho=ancho_de(FB_REC, AL), x=X, y=540, vel=0.4, nombre="clip_final_partido",
           src=FIN, rec=FB_REC)
    s.pon(etiqueta("ROMUALDO ARPPI FILHO", 30, fondo=ROJO), 1640, 260, w(2.69), rot=-1.5, nombre="arppi",
          sonido=PAPEL, hasta=w(5.8))
    s.pon(etiqueta("ÁRBITRO · BRASIL", 26), 1640, 360, w(3.0), rot=1, nombre="arppi_brasil", hasta=w(5.8))
    s.clip(474.0, w(5.8), 9.2, ancho=ancho_de(FB_REC, AL), x=X, y=540, vel=0.4, nombre="clip_campeon", src=FIN,
           rec=FB_REC, entrada="corte", dura=0.05)
    s.pon(marcador("3 - 2", "ARGENTINA CAMPEÓN DEL MUNDO", seed=287), 1560, 820, w(6.24), rot=-2, nombre="m32_campeon",
          entrada="golpe", dura=0.1, sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (9.2, 1.05, 900, 560)]


def c8_10():
    """(Sin narrador, 18 s: el festejo en el Azteca, uno encima de otro.)"""
    s = Escena("p9_10", 18.0)
    tramos = [(5857.5, 0.6, 2.6), (5866.0, 0.6, 2.6), (5871.0, 1.0, 2.4), (5890.0, 0.7, 2.4), (5940.0, 0.6, 3.0),
              (5926.0, 0.7, 2.4), (5930.0, 0.7, 2.6)]
    t = 0.0
    for k, (desde, vel, du) in enumerate(tramos):
        AL = 640 + (k % 3) * 40
        s.clip(desde, t, min(18.0, t + du + 2.0) if k < len(tramos) - 1 else 18.0, ancho=ancho_de(FC_REC, AL),
               x=W / 2 + (-1) ** k * (120 + (k % 3) * 60), y=540 + (-1) ** (k // 2) * 50, vel=vel,
               rot=(-1) ** k * (2 + k % 3), nombre=f"festejo_{k + 1}", src=FINC, rec=FC_REC, entrada="golpe", dura=0.12)
        t += du
    s.pon(C.sello("CAMPEONES DEL MUNDO", tam=96, rot=-5, seed=288), W / 2, 960, 14.5, nombre="sello_campeones",
          entrada="golpe", dura=0.08, sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (18.0, 1.06, W / 2, 540)]


CAPITULO8 = [c8_1, c8_2, c8_3, c8_4, c8_5, c8_6, c8_7, c8_8, c8_9, c8_10]


# ───── capítulo 9: El Mundial de Diego ─────
VOCES_C9 = ["6177bb720a847bc4", "b6a958480ad7b15f", REL / "tota.mp3", "51582bffd680213c", "e41810e5ade190ed",
            "74d4ee42f26b5de5", "1e9dcb4db6166cc8", "91066907c2d744ed", "cd5b01b921e7c5b2"]


def c9_1():
    """Diego levanta la copa: 5 goles, 5 asistencias y el Balón de Oro. Nunca un jugador había ganado un Mundial tan
    solo. Y nunca volvió a pasar."""
    s = Escena("p10_1", 13.0)
    fin_a = w(7.3)
    s.pon(foto(M / "maradona_copa.jpg", 860, seed=290), 1450, 540, w(0.0), rot=1, nombre="diego_levanta_copa",
          sonido=PAPEL, hasta=fin_a)
    s.pon(etiqueta("ESTADIO AZTECA", 28), 1450, 1010, w(1.44), rot=-1, nombre="azteca_copa", hasta=fin_a)
    s.pon(etiqueta("MARADONA EN MÉXICO 86", 28), 600, 140, w(0.3), rot=-1.5, nombre="maradona_86", hasta=fin_a)
    s.pon(titulo("5 goles", 120), 600, 320, w(2.46), nombre="cinco_goles", entrada="golpe", dura=0.1, sonido=SELLO,
          hasta=fin_a)
    s.pon(titulo("5 asistencias", 100), 600, 500, w(3.3), nombre="cinco_asistencias", entrada="golpe", dura=0.1,
          sonido=SELLO, hasta=fin_a)
    s.pon(etiqueta("BALÓN DE ORO DEL MUNDIAL", 34, fondo=ROJO), 600, 700, w(4.96), rot=1, nombre="balon_de_oro",
          sonido=PAPEL, hasta=fin_a)
    s.pon(foto(M / "diego_copa_espalda.png", 860, seed=291), 640, 540, w(7.38), rot=-1, nombre="diego_copa_espalda",
          sonido=PAPEL)
    s.pon(etiqueta("Y NUNCA VOLVIÓ A PASAR", 34, fondo=ROJO), 1450, 780, w(10.6), rot=-1.5, nombre="nunca_volvio")
    return s, [(0, 1.0, W / 2, H / 2), (w(7.3), 1.0, W / 2, H / 2), (13.0, 1.08, 760, 460)]


TOTA_FOTOS = [(M / "maradona_copa2.jpg", (60, 0, 660, 760), 540, 430), (M / "tota_diario.jpg", (700, 0, 1200, 675),
                                                                        1380, 430)]


def c9_2():
    """Unos minutos después, Diego salió al aire en una radio argentina. Del otro lado, en Buenos Aires, su mamá:
    doña Tota."""
    s = Escena("p10_2", 11.2)
    (f1, r1, x1, y1), (f2, r2, x2, y2) = TOTA_FOTOS
    s.pon(foto(f1, 660, caja=r1, seed=292), x1, y1, w(0.0), rot=-1.5, nombre="diego_radio", sonido=PAPEL)
    s.pon(etiqueta("ESTADIO AZTECA · MÉXICO", 26), x1, 820, w(0.3), rot=1, nombre="azteca_radio")
    s.pon(etiqueta("RADIO ARGENTINA · EN VIVO", 26, fondo=ROJO), x1, 910, w(4.01), rot=-1, nombre="en_vivo")
    im, cx, cy = trayecto([(800, 260), (1120, 260)])
    s.pon(im, cx, cy, w(5.86), nombre="linea_telefono", entrada="trazo", dura=0.8)
    s.pon(foto(f2, 660, caja=r2, seed=293), x2, y2, w(5.9), rot=1.5, nombre="tota_foto", sonido=PAPEL)
    s.pon(etiqueta("BUENOS AIRES", 26), x2, 820, w(7.37), rot=-1, nombre="buenos_aires")
    s.pon(etiqueta("DOÑA TOTA", 34, fondo=ROJO), x2, 910, w(9.32), rot=1.5, nombre="dona_tota")
    return s, [(0, 1.3, 640, 480), (w(5.8), 1.0, W / 2, H / 2), (11.2, 1.15, 1200, 480)]


def c9_3():
    """(La llamada real entre Diego y doña Tota, 21 s, con subtítulos.)"""
    s = Escena("p10_3", 21.4)
    (f1, r1, x1, y1), (f2, r2, x2, y2) = TOTA_FOTOS
    s.pon(foto(f1, 660, caja=r1, seed=292), x1, y1, 0.0, rot=-1.5, nombre="diego_llamada", entrada="corte", dura=0.05)
    s.pon(foto(f2, 660, caja=r2, seed=293), x2, y2, 0.0, rot=1.5, nombre="tota_llamada", entrada="corte", dura=0.05)
    im, cx, cy = trayecto([(800, 260), (1120, 260)])
    s.pon(im, cx, cy, 0.0, nombre="linea_llamada", entrada="corte", dura=0.05)
    lineas = [("—Hola, mamita. ¿Cómo estás, mamá?", 0, 0.1, 3.3), ("—Mi vida.", 1, 3.4, 6.0),
              ("—Te quiero mucho, mamá.", 0, 6.1, 7.9),
              ("—También, mi amor. Andá, descansá, mi hijo,\nque me hiciste la madre más feliz del mundo hoy.", 1, 8.0,
               16.0), ("—Yo juego para vos, mamá.", 0, 16.1, 18.2), ("—Sí, mi amor.", 1, 18.3, 20.8)]
    for k, (tx, quien, a, b) in enumerate(lineas):
        x = x1 if quien == 0 else x2
        if "\n" in tx:
            x = W / 2
        s.pon(titulo(tx, 44), x, 900, w(a), nombre=f"subtitulo_{k + 1}", dura=0.25, hasta=w(b))
    cam = [(0, 1.0, W / 2, H / 2)]
    for tx, quien, a, b in lineas:
        cx = 800 if quien == 0 else 1120
        cam += [(w(a), 1.08, cx, 520), (w(b) - 0.2, 1.08, cx, 520)]
    cam.append((21.4, 1.0, W / 2, H / 2))
    return s, cam


def c9_4():
    """La vuelta: Ezeiza, las rutas, las calles; el balcón de la Casa Rosada y la copa frente a una Plaza de Mayo
    repleta. Esa noche, el país entero salió a festejar."""
    s = Escena("p10_4", 16.8)
    s.pon(foto(M / "festejo_avion.jpg", 700, seed=294), W / 2, 540, w(0.0), rot=-1, nombre="festejo_avion",
          sonido=PAPEL, hasta=w(2.04))
    s.pon(etiqueta("LA VUELTA A BUENOS AIRES", 30, fondo=ROJO), W / 2, 950, w(0.27), rot=1, nombre="la_vuelta",
          hasta=w(2.04))
    fin_b = w(6.2)
    s.pon(foto(M / "eg_ezeiza.jpg", 760, seed=295), 520, 540, w(2.04), rot=-1.5, nombre="ezeiza_foto", sonido=PAPEL,
          hasta=fin_b)
    s.pon(etiqueta("EZEIZA", 40, fondo=ROJO), 520, 960, w(2.74), rot=1, nombre="ezeiza", hasta=fin_b)
    s.pon(etiqueta("EN LAS RUTAS", 40), 1350, 380, w(3.84), rot=-2, nombre="las_rutas", entrada="golpe", dura=0.08,
          sonido=PAPEL, hasta=fin_b)
    s.pon(etiqueta("EN LAS CALLES", 40), 1350, 560, w(5.14), rot=2, nombre="las_calles", entrada="golpe", dura=0.08,
          sonido=PAPEL, hasta=fin_b)
    s.pon(foto(M / "balcon.jpg", 680, seed=296), 720, 500, w(6.26), rot=-1, nombre="balcon_foto", sonido=PAPEL)
    s.pon(etiqueta("BALCÓN DE LA CASA ROSADA", 28), 720, 890, w(7.23), rot=1, nombre="casa_rosada")
    s.pon(etiqueta("PLAZA DE MAYO", 40, fondo=ROJO), 1600, 330, w(10.44), rot=-1.5, nombre="plaza_de_mayo",
          sonido=PAPEL)
    s.pon(C.sello("REPLETA", tam=100, rot=-6, seed=297), 1600, 520, w(11.4), nombre="repleta", entrada="golpe",
          dura=0.08, sonido=SELLO)
    s.pon(foto(M / "festejo_baires86.jpg", 360, seed=296), 1580, 820, w(12.76), rot=2, nombre="pais_entero",
          sonido=PAPEL)
    return s, [(0, 1.0, W / 2, H / 2), (w(6.2), 1.0, W / 2, H / 2), (16.8, 1.05, 900, 520)]


def c9_5():
    """Bilardo, el que todos querían echar, era campeón del mundo. Con el equipo feo, el que no le ganaba a nadie."""
    s = Escena("p10_5", 8.4)
    s.pon(foto(M / "eg_bilardo_festejo.jpg", 640, seed=298), 600, 520, w(0.0), rot=-1.5, nombre="bilardo_campeon",
          sonido=PAPEL)
    s.pon(etiqueta("CARLOS BILARDO", 34, fondo=ROJO), 600, 900, w(0.1), rot=1, nombre="bilardo_nombre_final")
    s.pon(etiqueta("EL QUE TODOS QUERÍAN ECHAR", 28), 1450, 200, w(0.92), rot=-1.5, nombre="querian_echar")
    s.pon(etiqueta("CON EL EQUIPO FEO", 34, fondo=ROJO), 1450, 680, w(4.4), rot=1, nombre="equipo_feo")
    s.pon(etiqueta("EL QUE NO LE GANABA A NADIE", 30), 1450, 800, w(5.26), rot=-1, nombre="no_le_ganaba")
    return s, [(0, 1.0, W / 2, H / 2), (8.4, 1.05, 900, 520)]


def c9_6():
    """La camiseta azul del DF: Diego la cambió con Hodge, que la guardó 36 años; en 2022 la subastó por más de 9
    millones de dólares. La más cara de la historia del deporte."""
    s = Escena("p10_6", 20.6)
    fin_a = w(3.9)
    s.clip(239.0, w(0.0), fin_a, ancho=ancho_de(FULL, 700), x=720, y=540, vel=0.35, nombre="clip_camiseta_azul_final",
           src=INGF, rec=FULL)
    s.pon(etiqueta("LA CAMISETA AZUL", 36, fondo=ROJO), 1600, 300, w(0.28), rot=-1.5, nombre="camiseta_azul_tira",
          sonido=PAPEL, hasta=fin_a)
    s.pon(etiqueta("COMPRADA EN UN NEGOCIO DEL DF", 26), 1600, 420, w(2.27), rot=1, nombre="comprada_df", hasta=fin_a)
    fin_b = w(11.3)
    s.pon(foto(M / "hodge_camiseta.jpg", 700, caja=(0, 88, 411, 601), seed=299), 460, 520, w(3.9), rot=-1.2,
          nombre="hodge_con_camiseta", sonido=PAPEL, hasta=fin_b)
    s.pon(etiqueta("STEVE HODGE", 34, fondo=ROJO), 460, 920, w(6.01), rot=1, nombre="hodge_nombre", hasta=fin_b)
    s.pon(foto(M / "nfm_manchester.jpg", 520, caja=(0, 22, 3800, 2378), seed=300), 1300, 560, w(8.8), rot=1,
          nombre="museo_manchester", sonido=PAPEL, hasta=fin_b)
    s.pon(etiqueta("NATIONAL FOOTBALL MUSEUM · MANCHESTER", 22), 1300, 860, w(9.0), rot=-1, nombre="museo_tira",
          hasta=fin_b)
    s.pon(titulo("36 años", 96), 1300, 170, w(9.52), nombre="treinta_y_seis", hasta=fin_b)
    s.pon(foto(M / "sothebys.jpg", 800, caja=(23, 0, 1920, 2592), seed=301), 460, 520, w(11.38), rot=-0.6,
          nombre="sothebys_foto", sonido=PAPEL)
    s.pon(etiqueta("SOTHEBY'S · LONDRES · MAYO 2022", 24), 460, 990, w(11.6), rot=1, nombre="sothebys_tira")
    billete = sin_blanco(COL / "billete_100.png", 110, seed=302)
    rng = np.random.default_rng(86)
    for k in range(22):
        t0 = w(13.8) + k * 0.07
        s.pon(billete, rng.uniform(820, 1860), -80, t0, rot=rng.uniform(-30, 30), nombre=f"billete_final_{k + 1}",
              entrada="corte", dura=0.05, mov=[(t0, t0 + 1.6, rng.uniform(-80, 80), 1250, "lineal",
                                                 rng.uniform(-90, 90))], hasta=t0 + 1.65,
              sonido=LLUVIA if k == 0 else False)
    s.pon(titulo("US$ 9,3\nmillones", 128), 1320, 340, w(13.72), nombre="nueve_millones", entrada="golpe", dura=0.1,
          sonido=SELLO)
    s.pon(etiqueta("£ 7.142.500", 34), 1320, 620, w(14.09), rot=-1, nombre="libras")
    s.pon(etiqueta("LA CAMISETA MÁS CARA DEL DEPORTE", 30, fondo=ROJO), 1320, 760, w(16.54), rot=1.5,
          nombre="mas_cara", sonido=PAPEL)
    return s, [(0, 1.0, W / 2, H / 2), (w(11.3), 1.0, W / 2, H / 2), (20.6, 1.05, 1100, 520)]


def c9_7():
    """Passarella, el capitán del 78, no jugó ni un minuto en México pero era parte del plantel: el único argentino
    con dos medallas. Por eso: 44 medallas de campeón del mundo para 43 jugadores."""
    s = Escena("p10_7", 25.2)
    fin_a = w(13.9)
    s.pon(foto(M / "diego_passarella_sombreros.jpg", 860, caja=(1060, 240, 1760, 1500), seed=303), 1400, 520, w(0.0),
          rot=1.2, nombre="passarella_sombrero", sonido=PAPEL, hasta=fin_a)
    s.pon(etiqueta("UN DATO MÁS", 28), 560, 120, w(0.06), rot=-1.5, nombre="un_dato_mas", hasta=fin_a)
    s.pon(etiqueta("DANIEL PASSARELLA", 40, fondo=ROJO), 560, 230, w(0.84), rot=1, nombre="passarella_nombre",
          sonido=PAPEL, hasta=fin_a)
    s.pon(etiqueta("1978 · CAMPEÓN, CAPITÁN", 32), 560, 370, w(2.29), rot=-1, nombre="p_1978", hasta=fin_a)
    s.pon(etiqueta("1986 · CAMPEÓN, SIN JUGAR", 32), 560, 470, w(5.34), rot=1, nombre="p_1986", hasta=fin_a)
    s.pon(etiqueta("EL ÚNICO ARGENTINO", 30, fondo=ROJO), 560, 620, w(9.93), rot=-1.5, nombre="unico_argentino",
          hasta=fin_a)
    s.pon(titulo("2 medallas.", 120), 560, 800, w(11.08), nombre="dos_medallas", entrada="golpe", dura=0.1,
          sonido=SELLO, hasta=fin_a)
    s.pon(etiqueta("DURANTE 36 AÑOS, UNA FRASE", 30), W / 2, 200, w(14.1), rot=-1, nombre="una_frase")
    s.pon(etiqueta("1978 + 1986", 40), W / 2, 330, w(17.53), rot=1, nombre="setenta_ocho_mas")
    s.pon(titulo("44 medallas", 150), W / 2, 500, w(19.04), nombre="cuarenta_y_cuatro", entrada="golpe", dura=0.1,
          sonido=SELLO)
    s.pon(titulo("para 43 jugadores.", 120), W / 2, 720, w(21.87), nombre="cuarenta_y_tres", entrada="golpe",
          dura=0.1, sonido=SELLO)
    return s, [(0, 1.0, W / 2, H / 2), (w(13.9), 1.0, W / 2, H / 2), (25.2, 1.06, W / 2, 560)]


def c9_8():
    """Pasaron 40 años. Argentina volvió a ser campeona en Qatar, con Messi. Pero México 86 siempre va a ser el
    Mundial de Diego: el de la mano, el del gol, el de los cuatro minutos."""
    s = Escena("p10_8", 14.7)
    fin_a = w(5.5)
    s.pon(foto(M / "eg_tapa_3482.jpg", 860, caja=(685, 980, 1336, 1914), seed=304), 1460, 540, w(0.3), rot=0.9,
          nombre="tapa_campeones", sonido=PAPEL, hasta=fin_a)
    s.pon(etiqueta("EL GRÁFICO · 1/7/1986", 22), 1460, 1010, w(0.5), rot=-1, nombre="credito_tapa_3482", hasta=fin_a)
    for k, (tx, t) in enumerate([("1978 · ARGENTINA", 0.6), ("1986 · MÉXICO", 2.04), ("2022 · QATAR · MESSI", 3.94)]):
        s.pon(etiqueta(tx, 34, fondo=ROJO if k == 1 else TINTA, seed=k), 560, 520 + k * 110, w(t), rot=(-1) ** k * 1.5,
              nombre=f"campeon_{k + 1}", sonido=PAPEL, hasta=fin_a)
    fin_b = w(9.9)
    s.clip(283.0, fin_a, fin_b, ancho=ancho_de(FULL, 760), x=W / 2, y=560, vel=0.35, nombre="clip_mundial_diego",
           src=INGF, rec=FULL)
    for k, (f, tx, t) in enumerate([(M / "mano_dios2.jpg", "LA MANO", 9.98), (M / "eludiendo_shilton.jpg", "EL GOL",
                                                                              10.79)]):
        x = 420 + k * 560
        s.pon(foto(f, 400, seed=305 + k), x, 480, w(t), rot=(-1) ** k * 2, nombre=f"ultimo_{k + 1}", sonido=PAPEL)
        s.pon(etiqueta(tx, 36, fondo=ROJO, seed=k), x, 740, w(t) + 0.1, rot=(-1) ** k * -1.5,
              nombre=f"ultimo_{k + 1}_tira")
    s.pon(titulo("51' · 55'", 110), 1540, 470, w(12.2), nombre="cuatro_minutos_fin", entrada="golpe", dura=0.1,
          sonido=SELLO)
    s.pon(etiqueta("LOS 4 MINUTOS", 36), 1540, 740, w(12.44), rot=1.5, nombre="los_cuatro_minutos")
    return s, [(0, 1.0, W / 2, H / 2), (w(9.9), 1.0, W / 2, H / 2), (14.7, 1.05, W / 2, 520)]


def c9_9():
    """Si llegaste hasta acá: suscribite, dejá tu like y contanos cuál es el mejor gol que viste. Te leemos. (+ 10 s
    para la pantalla final de YouTube)."""
    s = Escena("p10_9", 19.0)
    fin_a = w(9.0)
    s.pon(etiqueta("SI LLEGASTE HASTA ACÁ", 30), W / 2, 150, w(0.09), rot=-1, nombre="si_llegaste", hasta=fin_a)
    for k, (tx, t) in enumerate([("SUSCRIBITE", 0.94), ("LIKE", 2.62), ("COMENTÁ", 3.8)]):
        s.pon(etiqueta(tx, 60, fondo=ROJO if k == 0 else TINTA, seed=k), 480 + k * 480, 380, w(t), rot=(-1) ** k * 2,
              nombre=f"boton_{tx.lower()}", entrada="golpe", dura=0.1, sonido=SELLO, hasta=fin_a)
    s.pon(titulo("¿Cuál es el mejor gol\nque viste en tu vida?", 90), W / 2, 700, w(4.44), nombre="mejor_gol",
          hasta=fin_a)
    s.pon(etiqueta("TE LEEMOS", 34, fondo=ROJO), W / 2, 930, w(7.38), rot=1.5, nombre="te_leemos", hasta=fin_a)
    # pantalla final: el centro queda libre para las tarjetas de YouTube
    s.pon(C.sello("LOS 11", tam=150, rot=-5, seed=306), W / 2, 160, fin_a + 0.2, nombre="sello_los11",
          entrada="golpe", dura=0.08, sonido=SELLO)
    s.pon(etiqueta("ARGENTINA 1986 · EL MUNDIAL DE DIEGO", 28), W / 2, 980, fin_a + 0.5, rot=-1, nombre="cierre_tira")
    return s, [(0, 1.0, W / 2, H / 2), (19.0, 1.0, W / 2, H / 2)]


CAPITULO9 = [c9_1, c9_2, c9_3, c9_4, c9_5, c9_6, c9_7, c9_8, c9_9]


ESCENAS = [e1, e2, e3, e4, e5, e6, e7]

if __name__ == "__main__":
    a = sys.argv
    caps = {"--cap2": CAPITULO2, "--cap3": CAPITULO3, "--cap4": CAPITULO4, "--cap5": CAPITULO5, "--cap6": CAPITULO6,
            "--cap7": CAPITULO7, "--cap8": CAPITULO8, "--cap9": CAPITULO9}   # --capN: piezas p(N+1)_*
    lista = next((v for k, v in caps.items() if k in a), ESCENAS)
    cuales = range(1, len(lista) + 1) if a[1] == "todas" else [int(x) for x in a[1].split(",")]
    for n in cuales:
        s, cam = lista[n - 1]()
        print(s.render(capas="--capas" in a, camara=cam))
