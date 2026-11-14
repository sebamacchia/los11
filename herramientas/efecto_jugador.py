"""JUGADOR EN COLOR (edit de fútbol): fondo en blanco y negro, el jugador recortado en color, la pelota encendida,
destellos dibujados, estela de siluetas de colores, flash blanco + cuadro en blanco y negro puro, y vuelta al color.

Correr con el venv (rembg + numpy + scipy):
  herramientas/.venv/bin/python herramientas/efecto_jugador.py <video> <desde> <dur> <salida.mp4>
      [--vel 0.75] [--recorte x,y,w,h] [--color azul] [--flash 3.2]

- El jugador se ubica por el color de la camiseta (--color azul = Argentina 86 de suplente) y se recorta con
  u2net_human_seg sobre un recorte alrededor de él (mucho mejor que sobre el cuadro entero).
- La pelota se busca como mancha blanca y redonda fuera del jugador, siguiendo la posición anterior.
"""
import math
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps
from rembg import new_session, remove
from scipy import ndimage

W, H, FPS = 1920, 1080, 30
CELESTE, SOL, AZUL_OSC = (117, 170, 219), (246, 180, 14), (24, 44, 96)


def args():
    a = sys.argv[1:]
    op = {"vel": 0.75, "recorte": None, "color": "azul", "flash": 3.2, "pistas": None}
    pos = []
    i = 0
    while i < len(a):
        if a[i].startswith("--"):
            op[a[i][2:]] = a[i + 1]
            i += 2
        else:
            pos.append(a[i])
            i += 1
    return pos, op


def camiseta(a, color):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(-1), a.min(-1)
    sat = (mx - mn) / (mx + 1e-6)
    if color == "azul":
        m = (b > r + 0.12) & (b > g + 0.02) & (sat > 0.3) & (mx > 0.25)
    else:  # celeste y blanca: el celeste
        m = (b > r + 0.08) & (sat > 0.18) & (mx > 0.55)
    m[: int(a.shape[0] * 0.18)] = False  # arriba están los carteles
    return m


def interp(pts, k):
    """Posición (x, y) en el cuadro k (0-based) interpolando puntos [cuadro 1-based, x, y]."""
    pts = sorted(pts)
    f = k + 1
    if f <= pts[0][0]:
        return pts[0][1], pts[0][2]
    for a, b in zip(pts, pts[1:]):
        if f <= b[0]:
            u = (f - a[0]) / max(1, b[0] - a[0])
            return a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u
    return pts[-1][1], pts[-1][2]


def mascara_jugador(im, sesion, color, previo, punto=None):
    a = np.asarray(im).astype(np.float32) / 255
    m = camiseta(a, color)
    if punto is not None:  # seguimiento a mano: la camiseta es la que está en el punto
        cx, cy = punto
    else:
        lab, n = ndimage.label(m)
        if n == 0:
            return np.zeros(a.shape[:2], np.float32), previo
        tam = ndimage.sum(m, lab, range(1, n + 1))
        centros = ndimage.center_of_mass(m, lab, range(1, n + 1))
        mejor = max(range(n), key=lambda k: tam[k] - (0 if previo is None else
                                                        0.5 * math.dist(centros[k], previo)))
        cy, cx = centros[mejor]
    h, w = a.shape[:2]
    x0, y0 = int(max(0, cx - 150)), int(max(0, cy - 110))
    x1, y1 = int(min(w, cx + 150)), int(min(h, cy + 190))
    rec = im.crop((x0, y0, x1, y1))
    esc = 600 / max(rec.size)
    grande = rec.resize((int(rec.width * esc), int(rec.height * esc)), Image.LANCZOS)
    mm = remove(grande, session=sesion, only_mask=True).resize(rec.size, Image.BILINEAR)
    mm = np.asarray(mm).astype(np.float32) / 255
    # se queda con la mancha que toca la camiseta (saca rivales pegados)
    duro = mm > 0.5
    lab2, n2 = ndimage.label(duro)
    if n2 > 1:
        if punto is not None:  # la mancha más cercana al punto marcado
            py, px = int(cy - y0), int(cx - x0)
            dist = ndimage.distance_transform_edt(~(lab2 > 0), return_indices=True)[1]
            k = lab2[dist[0][py, px], dist[1][py, px]]
        else:
            cam = m[y0:y1, x0:x1]
            k = max(range(1, n2 + 1), key=lambda k: (cam & (lab2 == k)).sum())
        mm = mm * ndimage.binary_dilation(lab2 == k, iterations=3)
    # afina los bordes: el pasto no es jugador
    sub = a[y0:y1, x0:x1]
    pasto = (sub[..., 1] > sub[..., 0] + 0.06) & (sub[..., 1] > sub[..., 2] + 0.02)
    smx, smn = sub.max(-1), sub.min(-1)
    blanco = (smx > 0.68) & ((smx - smn) / (smx + 1e-6) < 0.22)  # la camiseta blanca del rival pegado
    pasto = ndimage.binary_dilation(pasto, iterations=1)
    mm = mm * (1 - pasto) * (1 - 0.9 * blanco)  # el pasto entre las piernas no se pinta
    out = np.zeros(a.shape[:2], np.float32)
    out[y0:y1, x0:x1] = mm
    return out, (cy, cx)


def pelota_pista(a, punto):
    x, y = punto
    x0, y0 = int(max(0, x - 30)), int(max(0, y - 30))
    sub = a[y0:int(y + 30), x0:int(x + 30)]
    luz = sub.mean(-1)
    if luz.size == 0 or luz.max() < 0.6:
        return (y, x, 12)
    m = luz > max(0.6, luz.max() - 0.15)
    yy, xx = np.nonzero(m)
    return (y0 + yy.mean(), x0 + xx.mean(), max(10, 1.2 * math.sqrt(len(xx) / math.pi) * 2))


def pelota(a, jugador, previo):
    mx, mn = a.max(-1), a.min(-1)
    sat = (mx - mn) / (mx + 1e-6)
    m = (mx > 0.78) & (sat < 0.28) & (jugador < 0.2)
    m[: int(a.shape[0] * 0.18)] = False
    lab, n = ndimage.label(m)
    cands = []
    for k, sl in enumerate(ndimage.find_objects(lab), 1):
        hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        area = (lab[sl] == k).sum()
        if 30 <= area <= 500 and 0.6 < ww / max(1, hh) < 1.7 and area > 0.5 * ww * hh:
            y0, y1 = max(0, sl[0].start - 6), sl[0].stop + 6
            x0, x1 = max(0, sl[1].start - 6), sl[1].stop + 6
            sub = a[y0:y1, x0:x1]
            anillo = ~(lab[y0:y1, x0:x1] == k)
            pasto = (sub[..., 1] > sub[..., 0] + 0.04) & (sub[..., 1] > sub[..., 2])
            if (pasto & anillo).sum() > 0.7 * anillo.sum():  # una pelota está sola en el pasto
                cands.append(((sl[0].start + sl[0].stop) / 2, (sl[1].start + sl[1].stop) / 2, max(ww, hh)))
    if not cands:
        return previo
    if previo is None:
        return max(cands, key=lambda c: c[0])  # la más baja (en el pasto)
    c = min(cands, key=lambda c: math.dist(c[:2], previo[:2]))
    return c if math.dist(c[:2], previo[:2]) < 90 else previo


def brillo(lienzo, pos, r, fuerza=1.0):
    """Pelota encendida: halo naranja + núcleo claro."""
    y, x = pos
    capa = Image.new("RGBA", lienzo.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    for k, (rr, col) in enumerate([(r * 3.2, (255, 120, 20, int(70 * fuerza))), (r * 2.1, (255, 150, 40, int(130 * fuerza))),
                                   (r * 1.35, (255, 200, 90, int(210 * fuerza)))]):
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col)
    capa = capa.filter(ImageFilter.GaussianBlur(r * 0.6))
    d = ImageDraw.Draw(capa)
    d.ellipse([x - r * 0.75, y - r * 0.75, x + r * 0.75, y + r * 0.75], fill=(255, 245, 220, int(255 * fuerza)))
    lienzo.alpha_composite(capa)


def destello(d, x, y, s, col=(255, 255, 255, 255)):
    """Estrella de cuatro puntas dibujada."""
    pts = []
    for k in range(8):
        ang = k * math.pi / 4 - math.pi / 2
        rr = s if k % 2 == 0 else s * 0.18
        pts.append((x + rr * math.cos(ang), y + rr * math.sin(ang)))
    d.polygon(pts, fill=col)


def chispa(d, x, y, s, col=(255, 255, 255, 255)):
    """Golpe en zigzag (contacto)."""
    pts = [(x - s, y - s * 0.3), (x - s * 0.3, y - s * 0.6), (x - s * 0.1, y - s * 0.1), (x + s * 0.5, y - s * 0.7),
           (x + s * 0.3, y + 0.0), (x + s, y - s * 0.2)]
    d.line(pts, fill=col, width=max(3, int(s * 0.16)), joint="curve")


def main():
    (video, desde, dur, salida), op = args()
    vel = float(op["vel"])
    tmp = Path(tempfile.mkdtemp())
    filtro = f"setpts=PTS/{vel},fps={FPS}"
    if op["recorte"]:
        x, y, w, h = op["recorte"].split(",")
        filtro = f"crop={w}:{h}:{x}:{y}," + filtro
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(desde), "-t", str(dur), "-i", video, "-vf", filtro,
                    str(tmp / "c_%04d.png")], check=True)
    cuadros = sorted(tmp.glob("c_*.png"))
    sesion = new_session("u2net_human_seg")
    import json
    pistas = json.loads(Path(op["pistas"]).read_text()) if op["pistas"] else {}
    mascaras, pelotas = [], []
    prev_j = prev_p = None
    for k, f in enumerate(cuadros):
        im = Image.open(f).convert("RGB")
        pj = interp(pistas["jugador"], k) if pistas.get("jugador") else None
        m, prev_j = mascara_jugador(im, sesion, op["color"], prev_j, pj)
        a = np.asarray(im).astype(np.float32) / 255
        if pistas.get("pelota"):
            prev_p = pelota_pista(a, interp(pistas["pelota"], k))
        else:
            prev_p = pelota(a, m, prev_p)
        mascaras.append(m)
        pelotas.append(prev_p)
        if k % 20 == 0:
            print(f"  recorte {k}/{len(cuadros)}", flush=True)
    sw, sh = Image.open(cuadros[0]).size
    esc = W / sw
    t_flash = float(op["flash"])
    f_flash = int(t_flash * FPS)
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                             "-pix_fmt", "yuv420p", salida], stdin=subprocess.PIPE)
    sombras = {}
    for k, f in enumerate(cuadros):
        col = Image.open(f).convert("RGB").resize((W, int(sh * esc)), Image.LANCZOS)
        if col.height != H:
            col = ImageOps.fit(col, (W, H), Image.LANCZOS)
        mk = Image.fromarray((mascaras[k] * 255).astype(np.uint8)).resize(col.size, Image.BILINEAR)
        mk = mk.filter(ImageFilter.GaussianBlur(1.2))
        bola = pelotas[k]
        if k < f_flash:
            gris = ImageOps.grayscale(col)
            gris = ImageEnhance.Contrast(gris).enhance(1.25).point(lambda v: int(v * 0.82))
            lienzo = Image.merge("RGB", [gris] * 3).convert("RGBA")
            # estela: siluetas de colores de cuadros anteriores, detrás del jugador
            if k >= int(f_flash * 0.45):
                ys_, xs_ = np.nonzero(mascaras[k] > 0.5)
                lado = 1
                if len(xs_) and bola:  # corre hacia la pelota: la estela va del otro lado
                    lado = 1 if bola[1] < xs_.mean() else -1
                crece = min(1.0, (k - int(f_flash * 0.45)) / 8)
                silueta = mk.point(lambda v: 255 if v > 110 else 0).filter(ImageFilter.GaussianBlur(0.8))
                for n, color in [(3, AZUL_OSC), (2, SOL), (1, CELESTE)]:
                    dx = int(lado * n * 15 * crece)
                    dy = int(-n * 3 * crece)
                    capa = Image.new("RGBA", col.size, color + (255,))
                    capa.putalpha(ImageChops.offset(silueta, dx, dy))
                    lienzo.alpha_composite(capa)
            r_, g_, b_ = col.split()  # el video tiene dominante verde (rebote del pasto): se la saca al jugador
            vivo = Image.merge("RGB", (r_.point(lambda v: min(255, int(v * 1.06))), g_.point(lambda v: int(v * 0.9)), b_))
            vivo = ImageEnhance.Color(vivo).enhance(1.15).convert("RGBA")
            vivo.putalpha(mk)
            lienzo.alpha_composite(vivo)
            # destellos y golpes, cerca del jugador
            ys, xs = np.nonzero(mascaras[k] > 0.5)
            if len(xs):
                bx0, bx1 = xs.min() * esc, xs.max() * esc
                by0, by1 = ys.min() * esc, ys.max() * esc
                d = ImageDraw.Draw(lienzo)
                for (f0, fx, fy, s) in [(4, 1.15, 0.85, 34), (22, -0.2, 0.25, 46), (40, 1.05, 0.15, 30),
                                        (58, -0.15, 0.9, 40), (76, 1.1, 0.5, 36)]:
                    e = k - f0
                    if 0 <= e < 9:
                        sc = math.sin(math.pi * e / 9)
                        destello(d, bx0 + (bx1 - bx0) * fx, by0 + (by1 - by0) * fy, s * sc)
                for (f0, fx, fy, s) in [(30, 1.2, 0.35, 38), (66, -0.25, 0.55, 34)]:
                    e = k - f0
                    if 0 <= e < 6:
                        chispa(d, bx0 + (bx1 - bx0) * fx, by0 + (by1 - by0) * fy, s)
            if bola:
                brillo(lienzo, (bola[0] * esc, bola[1] * esc), max(10, bola[2] * esc * 0.55))
            cuadro = lienzo.convert("RGB")
        elif k < f_flash + 2:  # flash: el jugador en blanco puro
            gris = Image.merge("RGB", [ImageOps.grayscale(col).point(lambda v: int(v * 0.6))] * 3).convert("RGBA")
            blanco = Image.new("RGBA", col.size, (255, 255, 255, 255))
            blanco.putalpha(mk.point(lambda v: 255 if v > 90 else 0))
            gris.alpha_composite(blanco)
            cuadro = gris.convert("RGB")
        elif k < f_flash + 5:  # cuadro de fotocopia: blanco y negro puro
            g = ImageOps.grayscale(col).filter(ImageFilter.GaussianBlur(1))
            cuadro = Image.merge("RGB", [g.point(lambda v: 0 if v < 70 else 255)] * 3)
        else:  # vuelve el color
            lienzo = col.convert("RGBA")
            if bola:
                brillo(lienzo, (bola[0] * esc, bola[1] * esc), max(10, bola[2] * esc * 0.55), 0.8)
            cuadro = lienzo.convert("RGB")
        proc.stdin.write(cuadro.tobytes())
    proc.stdin.close()
    proc.wait()
    print("listo:", salida)


if __name__ == "__main__":
    main()
