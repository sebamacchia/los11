"""DIBUJO (edit de fútbol, pedido 14/11 para el gol del siglo): la jugada pasada a dibujo sobre un fondo liso.
- Los de camiseta azul (Argentina) quedan pintados en color, con look de ilustración (colores planos + trazo).
- Los rivales (camiseta blanca) quedan como siluetas de línea blanca, vacías.
- Las líneas de la cancha y el arco salen del video (lo blanco y fino) y se dibujan como trazos.
- La pelota, blanca y llena.
Jugadores grandes: recorte con rembg (u2net_human_seg) alrededor de cada mancha; chicos: la mancha de color.

  herramientas/.venv/bin/python herramientas/efecto_dibujo.py <video> <desde> <dur> <salida.mp4> [--vel 1] [--fondo 150,22,48]
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter
from scipy import ndimage
from rembg import new_session, remove

W, H, FPS = 1920, 1080, 30
CW, CH = 960, 540  # resolución de trabajo de las máscaras


def args():
    a = sys.argv[1:]
    op = {"vel": 1.0, "fondo": "150,22,48"}
    pos, i = [], 0
    while i < len(a):
        if a[i].startswith("--"):
            op[a[i][2:]] = a[i + 1]
            i += 2
        else:
            pos.append(a[i])
            i += 1
    return pos, op


def fondo_liso(color):
    y, x = np.mgrid[0:H, 0:W]
    r = np.sqrt(((x - W * 0.5) / W) ** 2 + ((y - H * 0.42) / H) ** 2)
    luz = np.clip(1.12 - r * 0.55, 0.7, 1.12)[..., None]
    rng = np.random.default_rng(1)
    grano = ndimage.gaussian_filter(rng.standard_normal((H, W)), 1.0)[..., None] * 2.2
    return Image.fromarray(np.clip(np.array(color) * luz + grano, 0, 255).astype(np.uint8))


def tope_cancha(pasto):
    """Por columna, la primera fila desde la que los 40 px de abajo son casi todo pasto (arriba: carteles y tribuna)."""
    h, w = pasto.shape
    vent = 40
    c = np.cumsum(np.vstack([np.zeros((1, w)), pasto.astype(np.float32)]), axis=0)
    frac = (c[np.minimum(np.arange(h) + vent, h)] - c[np.arange(h)]) / np.maximum(1, np.minimum(vent, h - np.arange(h)))[:, None]
    ok = frac > 0.8
    tope = np.where(ok.any(0), ok.argmax(0), h)
    tope = ndimage.median_filter(tope, size=31)  # sin saltos por un jugador alto
    return np.arange(h)[:, None] >= tope[None, :]


def analizar(a, full, sesion):
    """Recorte por color (croma del pasto) a resolución completa, clasificado por mancha:
    fina y larga = línea; chica y redonda = pelota; con camiseta azul = Argentina (con la red si es grande);
    el resto = rival. Devuelve máscaras (azules, blancos, lineas, pelota)."""
    F = np.asarray(full).astype(np.float32) / 255
    fr, fg, fb = F[..., 0], F[..., 1], F[..., 2]
    fmx, fmn = F.max(-1), F.min(-1)
    fsat = (fmx - fmn) / (fmx + 1e-6)
    f_pasto = (fg > fr + 0.04) & (fg > fb + 0.01) & (fsat > 0.16) & (fmx > 0.22)
    f_azul = (fb > fr + 0.1) & (fb > fg + 0.02) & (fsat > 0.25)
    f_blanco = (fmx > 0.58) & (fsat < 0.28)
    z = np.zeros((H, W), bool)
    cancha = tope_cancha(ndimage.binary_opening(f_pasto[::2, ::2], iterations=2))
    cancha = np.asarray(Image.fromarray(cancha.astype(np.uint8) * 255).resize((W, H))) > 0
    cancha = ndimage.binary_erosion(cancha, iterations=6)
    if cancha.mean() < 0.15:
        return z, z, z, z
    crudo = cancha & ~f_pasto
    otro = ndimage.binary_opening(crudo)  # solo ruido de un pixel
    # lo fino (líneas, arco) se separa de lo grueso (cuerpos): apertura con un disco de radio 3 y reconstrucción
    disco = ndimage.generate_binary_structure(2, 1)
    nucleo = ndimage.binary_opening(otro, structure=disco, iterations=3)
    cuerpos = otro & ndimage.binary_dilation(nucleo, structure=disco, iterations=4)
    piernas = crudo & ~cuerpos & ndimage.binary_dilation(cuerpos, iterations=7)  # lo fino pegado a un cuerpo
    piernas &= ~(ndimage.uniform_filter(otro.astype(np.float32), size=31) < 0.06)
    cuerpos |= piernas
    lineas = otro & ~cuerpos
    lab, n = ndimage.label(ndimage.binary_closing(cuerpos, iterations=2) & cancha)
    azules, blancos, pelota = z.copy(), z.copy(), z.copy()
    for k, s in enumerate(ndimage.find_objects(lab), 1):
        m = lab[s] == k
        area = m.sum()
        hh, ww = s[0].stop - s[0].start, s[1].stop - s[1].start
        if area < 50 or ww > 0.22 * W:  # motas y los carteles del fondo
            continue
        bl = f_blanco[s][m].mean()
        if area < 700 and 0.6 < ww / max(1, hh) < 1.7 and area > 0.5 * ww * hh and bl > 0.45 and hh < 34:
            pelota[s] |= m
            continue
        y0, y1, x0, x1 = s[0].start, s[0].stop, s[1].start, s[1].stop
        mm = m
        az = f_azul[s] & mm
        wh = f_blanco[s] & mm
        if hh >= 130 and az.sum() > 0.05 * mm.sum():  # Argentino grande: recorte fino con la red
            py, px = int(hh * 0.1) + 8, int(ww * 0.15) + 8
            Y0, Y1, X0, X1 = max(0, y0 - py), min(H, y1 + py), max(0, x0 - px), min(W, x1 + px)
            rec = full.crop((X0, Y0, X1, Y1))
            esc = max(1.0, 420 / max(rec.size))
            big = rec.resize((int(rec.width * esc), int(rec.height * esc)), Image.LANCZOS)
            red = np.asarray(remove(big, session=sesion, only_mask=True).resize(rec.size, Image.BILINEAR)) > 120
            red = red[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0]
            mm = (mm & ndimage.binary_dilation(red, iterations=3)) | (red & ~f_pasto[s])
            az, wh = f_azul[s] & mm, f_blanco[s] & mm
        if az.sum() < 0.05 * mm.sum():
            if wh.sum() > 0.12 * mm.sum():  # un rival tiene camiseta blanca; si no, es una mancha del pasto
                blancos[s] |= mm
        elif wh.sum() < 0.1 * mm.sum():
            azules[s] |= mm
        else:  # jugadores pegados: cada pixel va con la camiseta más cercana
            da = ndimage.distance_transform_edt(~az)
            dw = ndimage.distance_transform_edt(~ndimage.binary_opening(wh, iterations=2))
            azules[s] |= mm & (da <= dw)
            blancos[s] |= mm & (da > dw)
    # líneas finas que el croma no separa: más claras que el pasto de alrededor (top-hat a media resolución)
    luz = a.mean(-1)
    th = luz - ndimage.grey_opening(luz, size=(7, 7))
    sat = (a.max(-1) - a.min(-1)) / (a.max(-1) + 1e-6)
    ch = cancha[::2, ::2]
    fin = ch & (th > 0.06) & (sat < 0.4)
    lab, n = ndimage.label(fin, structure=np.ones((3, 3)))
    if n:
        sl = ndimage.find_objects(lab)
        largo = np.array([max(t[0].stop - t[0].start, t[1].stop - t[1].start) for t in sl])
        fin = np.isin(lab, np.nonzero(largo >= 35)[0] + 1)
        fin = np.asarray(Image.fromarray(fin.astype(np.uint8) * 255).resize((W, H), Image.BILINEAR)) > 100
        lineas |= fin & ~ndimage.binary_dilation(azules | blancos, iterations=4)
    lab, n = ndimage.label(lineas, structure=np.ones((3, 3)))
    if n:  # una línea de cancha es larga (las letras de los carteles, no)
        sl = ndimage.find_objects(lab)
        largo = np.array([max(t[0].stop - t[0].start, t[1].stop - t[1].start) for t in sl])
        lineas = np.isin(lab, np.nonzero(largo >= 80)[0] + 1)
    return azules, blancos, lineas, pelota


def a_grande(m, blur=1.0):
    im = Image.fromarray((m * 255).astype(np.uint8))
    return im.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: 255 if v > 110 else int(v * 1.6))


def pintado(im):
    """Look de ilustración: colores planos, un poco más saturados, con trazo oscuro."""
    p = im.filter(ImageFilter.ModeFilter(7)).filter(ImageFilter.SMOOTH_MORE)
    r, g, b = p.split()
    p = Image.merge("RGB", (r.point(lambda v: min(255, int(v * 1.06))), g.point(lambda v: int(v * 0.9)), b))
    p = ImageEnhance.Color(p).enhance(1.35)
    p = ImageEnhance.Contrast(p).enhance(1.15)
    q = np.asarray(p).astype(np.int16)
    q = (q // 28) * 28 + 14  # posterizado suave
    p = Image.fromarray(np.clip(q, 0, 255).astype(np.uint8))
    bordes = ImageEnhance.Contrast(im.convert("L").filter(ImageFilter.FIND_EDGES)).enhance(2.2)
    bordes = bordes.point(lambda v: 255 if v > 120 else 0).filter(ImageFilter.GaussianBlur(0.7))
    return ImageChops.subtract(p, Image.merge("RGB", [bordes.point(lambda v: int(v * 0.55))] * 3))


def main():
    (video, desde, dur, salida), op = args()
    vel = float(op["vel"])
    color = tuple(int(c) for c in op["fondo"].split(","))
    tmp = Path(tempfile.mkdtemp())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(desde), "-t", str(dur), "-i", video, "-vf",
                    f"scale={W}:{H},setpts=PTS/{vel},fps={FPS}", str(tmp / "c_%04d.png")], check=True)
    cuadros = sorted(tmp.glob("c_*.png"))
    base = fondo_liso(color)
    sesion = new_session("u2net_human_seg")
    linea_col = tuple(min(255, int(c + (255 - c) * 0.55)) for c in color)  # trazo de cancha: el fondo aclarado
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
                             "-pix_fmt", "yuv420p", salida], stdin=subprocess.PIPE)
    for k, f in enumerate(cuadros):
        im = Image.open(f).convert("RGB")
        a = np.asarray(im.resize((CW, CH), Image.BILINEAR)).astype(np.float32) / 255
        azules, blancos, lineas, pelota = analizar(a, im, sesion)
        lienzo = base.copy()
        # líneas de cancha y arco
        trazo = Image.fromarray((lineas * 255).astype(np.uint8))
        lienzo.paste(linea_col, (0, 0, W, H), trazo.filter(ImageFilter.GaussianBlur(0.8)).point(lambda v: min(255, v * 2)))
        # rivales: solo el contorno, en blanco
        mb = a_grande(blancos, 1.2)
        contorno = ImageChops.subtract(mb.filter(ImageFilter.MaxFilter(5)), mb)
        lienzo.paste((250, 246, 240), (0, 0, W, H), contorno.filter(ImageFilter.GaussianBlur(0.6)))
        # Argentina: pintados
        ma = a_grande(azules, 1.0)
        lienzo.paste(pintado(im), (0, 0), ma)
        # pelota
        if pelota.any():
            ys, xs = np.nonzero(pelota)
            cx, cy = xs.mean(), ys.mean()
            rr = max(7, np.sqrt(len(xs) / np.pi) * 0.95)
            d = ImageDraw.Draw(lienzo)
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(248, 248, 244))
            d.arc([cx - rr * 0.7, cy - rr * 0.7, cx + rr * 0.7, cy + rr * 0.7], 200, 300, fill=(40, 70, 150),
                  width=max(2, int(rr * 0.3)))
        proc.stdin.write(lienzo.tobytes())
        if k % 30 == 0:
            print(f"  {k}/{len(cuadros)}", flush=True)
    proc.stdin.close()
    proc.wait()
    print("listo:", salida)


if __name__ == "__main__":
    main()
