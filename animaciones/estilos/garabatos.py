"""Garabatos dibujados a mano alrededor de un jugador recortado (estilo "doodle").

    /usr/bin/python3 garabatos.py assets/brazos_cut.webm assets/brazos_garabatos.webm [color]

Lee la máscara del recorte cuadro por cuadro, busca el contorno del jugador y dibuja trazos
cortos hacia afuera (líneas de acción) más un "halo" ondulado sobre la cabeza. Los trazos se
redibujan cada 3 cuadros con otra semilla, para que "tiemblen" como animación a mano.
Todo es determinístico: la semilla sale del número de cuadro.
"""
import math
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ENTRADA, SALIDA = sys.argv[1], sys.argv[2]
COLOR = sys.argv[3] if len(sys.argv) > 3 else "#22c3f3"
W, H, ESC = 1920, 1080, 4          # se analiza a 480x270 (ESC = 4)
BINS = 16                          # cantidad de trazos alrededor del cuerpo
CADA = 3                           # cuadros que dura cada dibujo antes de "temblar"

tmp = Path(tempfile.mkdtemp())
subprocess.run(["ffmpeg", "-v", "error", "-c:v", "libvpx-vp9", "-i", ENTRADA, "-vf", f"scale={W // ESC}:{H // ESC}",
                "-pix_fmt", "rgba", str(tmp / "m%04d.png")], check=True)
mascaras = sorted(tmp.glob("m*.png"))


def contorno(alfa):
    m = Image.fromarray(((alfa > 110) * 255).astype(np.uint8))
    dil = np.array(m.filter(ImageFilter.MaxFilter(9))) > 0
    ero = np.array(m.filter(ImageFilter.MaxFilter(5))) > 0
    borde = dil & ~ero
    ys, xs = np.nonzero(borde)
    return xs, ys, np.array(m) > 0


def trazo(d, puntos, ancho):
    d.line(puntos, fill=COLOR, width=ancho, joint="curve")
    for x, y in (puntos[0], puntos[-1]):
        r = ancho / 2
        d.ellipse([x - r, y - r, x + r, y + r], fill=COLOR)


for k, f in enumerate(mascaras):
    alfa = np.array(Image.open(f))[:, :, 3]
    lienzo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lienzo)
    xs, ys, cuerpo = contorno(alfa)
    if len(xs) > 40:
        cx, cy = xs.mean(), ys.mean()
        rnd = random.Random(1000 + k // CADA)
        ang = np.arctan2(ys - cy, xs - cx)
        dist = np.hypot(xs - cx, ys - cy)
        for b in range(BINS):
            a0 = -math.pi + b * 2 * math.pi / BINS
            sel = (ang >= a0) & (ang < a0 + 2 * math.pi / BINS)
            if not sel.any():
                continue
            i = np.argmax(np.where(sel, dist, -1))
            px, py = xs[i] * ESC, ys[i] * ESC
            if py > H - 40:            # nada pegado al borde de abajo
                continue
            a = math.atan2(py - cy * ESC, px - cx * ESC) + rnd.uniform(-0.18, 0.18)
            gap = rnd.uniform(28, 52)
            largo = rnd.uniform(60, 135)
            # cada trazo es una línea apenas curva, en 4 puntos
            pts = []
            for t in np.linspace(0, 1, 4):
                r = gap + largo * t
                curva = math.sin(t * math.pi) * rnd.uniform(-10, 10)
                pts.append((px + math.cos(a) * r - math.sin(a) * curva + rnd.uniform(-2, 2),
                            py + math.sin(a) * r + math.cos(a) * curva + rnd.uniform(-2, 2)))
            trazo(d, pts, rnd.choice([12, 14, 16]))
        # líneas que acompañan la silueta, un poco afuera del cuerpo
        for _ in range(3):
            a0 = rnd.uniform(-math.pi, math.pi)
            sel = (ang >= a0) & (ang < a0 + 0.45)
            if sel.sum() < 6:
                continue
            idx = np.nonzero(sel)[0]
            idx = idx[np.argsort(ang[idx])]
            pts = []
            for j in idx[:: max(1, len(idx) // 9)]:
                if dist[j] < dist[sel].max() * 0.85:
                    continue
                a = ang[j]
                pts.append((xs[j] * ESC + math.cos(a) * 30, ys[j] * ESC + math.sin(a) * 30))
            if len(pts) >= 3 and max(p[1] for p in pts) < H - 40:
                trazo(d, pts, 12)
        # halo ondulado sobre el punto más alto del cuerpo
        top = np.argmin(ys)
        hx, hy = xs[top] * ESC, ys[top] * ESC - rnd.uniform(38, 52)
        if hy > 30:
            ancho = rnd.uniform(150, 190)
            onda = [(hx - ancho / 2 + ancho * t, hy + math.sin(t * math.pi * 3 + rnd.uniform(0, 1)) * 12 - math.sin(t * math.pi) * 22)
                    for t in np.linspace(0, 1, 28)]
            trazo(d, onda, 14)
    lienzo.save(tmp / f"g{k:04d}.png")

subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i", str(tmp / "g%04d.png"),
                "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "4M", "-auto-alt-ref", "0", SALIDA], check=True)
shutil.rmtree(tmp)
print(SALIDA, len(mascaras), "cuadros")
