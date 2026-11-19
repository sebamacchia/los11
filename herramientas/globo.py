"""GLOBO — la Tierra en 3D (proyección ortográfica real sobre la textura de la NASA) con cámara que baja desde el
espacio hasta un país y lo marca (17/11, nota del usuario en el Vibe Editor: "¿no se puede hacer una animación desde
la estratósfera a México? y cuando decís México que se muestre en el mapa").

  g = Globo(pais="Mexico", centro=(23.0, -102.0))
  img = g.cuadro(t)      # RGBA 1920x1080 con transparencia alrededor del globo

Texturas: material/intro/tierra_topo.jpg (NASA "Land shallow topo", 21600x10800, dominio público): una versión chica
para el globo entero y un recorte en alta alrededor del país para cuando la cámara está cerca. Forma del país:
Natural Earth 50m (.cache/geo/ne_50m_countries.geojson, dominio público).
Prueba: herramientas/.venv/bin/python herramientas/globo.py <salida.mp4>
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

RAIZ = Path(__file__).resolve().parent.parent
TEX = RAIZ / "proyectos/argentina-1986/material/intro/tierra_topo.jpg"
GEO = RAIZ / ".cache/geo/ne_50m_countries.geojson"
W, H = 1920, 1080
Image.MAX_IMAGE_PIXELS = None


def suave(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def _poligonos(pais):
    d = json.loads(GEO.read_text())
    f = next(f for f in d["features"] if f["properties"].get("ADMIN") == pais)
    g = f["geometry"]
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    return [np.array(p[0], dtype=float) for p in polys]          # solo el anillo exterior (lon, lat)


class Globo:
    def __init__(self, pais="Mexico", centro=(23.0, -102.0), desde_lon=-68.0, r0=330, r1=2250, cx=960, cy=540,
                 t_zoom=(0.25, 1.95), t_marca=2.0, recorte=(-5, 55, -135, -65)):
        """r0/r1: radio del globo al principio y al final (px); t_zoom: cuándo baja la cámara (s, desde que aparece);
        t_marca: cuándo se marca el país; recorte: (lat_min, lat_max, lon_min, lon_max) de la textura en alta."""
        self.lat0, self.lon1 = map(math.radians, centro)
        self.lon_ini = math.radians(desde_lon)
        self.r0, self.r1, self.cx, self.cy = r0, r1, cx, cy
        self.t_zoom, self.t_marca = t_zoom, t_marca
        big = Image.open(TEX).convert("RGB")
        self.chica = np.asarray(big.resize((5400, 2700), Image.LANCZOS))
        la0, la1, lo0, lo1 = recorte
        px = big.width / 360
        caja = (int((lo0 + 180) * px), int((90 - la1) * px), int((lo1 + 180) * px), int((90 - la0) * px))
        self.alta = np.asarray(big.crop(caja))
        self.rec = recorte
        del big
        self.polys = [np.radians(p) for p in _poligonos(pais)]
        yy, xx = np.mgrid[0:H, 0:W]
        self.xx, self.yy = xx.astype(np.float32), yy.astype(np.float32)

    def camara(self, t):
        a, b = self.t_zoom
        u = suave((t - a) / (b - a))
        r = self.r0 * (self.r1 / self.r0) ** u                    # zoom exponencial: se siente como bajar
        lon0 = self.lon_ini + (self.lon1 - self.lon_ini) * suave((t - a) / (b - a) * 1.25)
        return r, lon0

    def _proyectar(self, lon, lat, r, lon0):
        c0, s0 = math.cos(self.lat0), math.sin(self.lat0)
        x = r * np.cos(lat) * np.sin(lon - lon0)
        y = r * (c0 * np.sin(lat) - s0 * np.cos(lat) * np.cos(lon - lon0))
        vis = s0 * np.sin(lat) + c0 * np.cos(lat) * np.cos(lon - lon0)
        return self.cx + x, self.cy - y, vis

    def pantalla(self, lat, lon, t):
        """(lat, lon) en grados -> (x, y) en pantalla en el instante t (para poner tiras o líneas encima)."""
        r, lon0 = self.camara(t)
        x, y, _ = self._proyectar(np.radians(lon), np.radians(lat), r, lon0)
        return float(x), float(y)

    def cuadro(self, t):
        r, lon0 = self.camara(t)
        X = (self.xx - self.cx) / r
        Y = (self.cy - self.yy) / r
        rho2 = X * X + Y * Y
        dentro = rho2 < 1.0
        z = np.sqrt(np.clip(1 - rho2, 0, 1))
        c0, s0 = math.cos(self.lat0), math.sin(self.lat0)
        lat = np.arcsin(np.clip(z * s0 + Y * c0, -1, 1))
        lon = lon0 + np.arctan2(X, z * c0 - Y * s0)
        lon = (lon + np.pi) % (2 * np.pi) - np.pi
        latd, lond = np.degrees(lat), np.degrees(lon)
        # textura: en alta dentro del recorte, si no la chica
        la0, la1, lo0, lo1 = self.rec
        hi = dentro & (latd > la0) & (latd < la1) & (lond > lo0) & (lond < lo1)
        h, w = self.chica.shape[:2]
        img = self.chica[np.clip(((90 - latd) / 180 * h).astype(int), 0, h - 1),
                         np.clip(((lond + 180) / 360 * w).astype(int), 0, w - 1)].astype(np.float32)
        if hi.any():
            ha, wa = self.alta.shape[:2]
            fy = ((la1 - latd[hi]) / (la1 - la0) * ha).astype(int).clip(0, ha - 1)
            fx = ((lond[hi] - lo0) / (lo1 - lo0) * wa).astype(int).clip(0, wa - 1)
            img[hi] = self.alta[fy, fx]
        # luz: borde más oscuro (se ve esférico) + un poco de brillo arriba a la izquierda
        luz = 0.5 + 0.5 * z + 0.12 * np.clip((-X + Y) * z, -1, 1)
        img *= luz[..., None]
        # el país: al marcarlo, el resto se apaga y México queda rojo
        m = suave((t - self.t_marca) / 0.3)
        if m > 0:
            capa = Image.new("L", (W, H), 0)
            d = ImageDraw.Draw(capa)
            bordes = []
            for p in self.polys:
                px_, py_, vis = self._proyectar(p[:, 0], p[:, 1], r, lon0)
                if (vis > 0).mean() < 0.5:
                    continue
                pts = list(zip(px_.tolist(), py_.tolist()))
                d.polygon(pts, fill=255)
                bordes.append(pts)
            mk = np.asarray(capa.filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32)[..., None] / 255
            rojo = np.array([178, 38, 30], np.float32)
            gris = img.mean(axis=2, keepdims=True)
            fuera = img * (1 - 0.55 * m) * 0.7 + gris * 0.3 * (1 - 0.55 * m)
            pais = img * (1 - 0.55 * m) + rojo * 0.55 * m
            img = fuera * (1 - mk) + pais * mk
        out = np.clip(img, 0, 255).astype(np.uint8)
        alfa = np.clip((1 - np.sqrt(rho2)) * r * 0.9, 0, 1)      # borde suave, sin línea blanca
        im = Image.fromarray(np.dstack([out, (alfa * 255).astype(np.uint8)]), "RGBA")
        if m > 0:
            d = ImageDraw.Draw(im)
            for pts in bordes:
                d.line(pts + [pts[0]], fill=(242, 238, 228, int(255 * m)), width=5, joint="curve")
        # atmósfera: un halo azul fino cuando el globo se ve entero
        if r < 900:
            halo = Image.new("L", (W, H), 0)
            ImageDraw.Draw(halo).ellipse((self.cx - r - 14, self.cy - r - 14, self.cx + r + 14, self.cy + r + 14),
                                         outline=255, width=16)
            halo = halo.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.6 * (1 - r / 900)))
            fondo = Image.new("RGBA", (W, H), (120, 180, 255, 0))
            fondo.putalpha(halo)
            fondo.alpha_composite(im)
            im = fondo
        return im


if __name__ == "__main__":
    salida = Path(sys.argv[1])
    g = Globo()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", "30", "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(salida)],
                         stdin=subprocess.PIPE)
    fondo = Image.new("RGBA", (W, H), (60, 52, 44, 255))
    for k in range(int(3.2 * 30)):
        f = fondo.copy()
        f.alpha_composite(g.cuadro(k / 30))
        p.stdin.write(f.convert("RGB").tobytes())
    p.stdin.close()
    p.wait()
    print(salida)
