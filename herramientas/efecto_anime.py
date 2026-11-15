"""ANIME (pedido 14/11 para el gol del siglo): la jugada pasada a dibujo animado de los 80 (cel pintado, trazo de tinta,
colores planos y saturados, animación "en dos/tres") y después gastada como una cinta VHS vieja: imagen que baila,
color corrido, grano, rayas, polvo, barra de tracking y cortes rotos de cinta.

  herramientas/.venv/bin/python herramientas/efecto_anime.py <video> <desde> <dur> <salida.mp4>
      [--vel 1] [--tiempos 2] [--suciedad 1] [--semilla 7]

--tiempos: cada dibujo se repite N cuadros (2 = 15 dibujos/s, 3 = 10: más "anime barato").
--suciedad: 0 = anime limpio, 1 = VHS gastado, 1.6 = cinta destruida.
"""
import subprocess
import sys

import cv2
import numpy as np

W, H, FPS = 1920, 1080, 30
TW, TH = 960, 540  # resolución del "dibujo"


def args():
    a = sys.argv[1:]
    op = {"vel": "1", "tiempos": "2", "suciedad": "1", "semilla": "7"}
    pos, i = [], 0
    while i < len(a):
        if a[i].startswith("--"):
            op[a[i][2:]] = a[i + 1]
            i += 2
        else:
            pos.append(a[i])
            i += 1
    return pos, op


# ---------------------------------------------------------------- dibujo (cel)
def cel(rgb):
    """Frame 960x540 RGB -> (color plano, máscara de tinta)."""
    img = rgb
    for _ in range(3):
        img = cv2.bilateralFilter(img, 9, 40, 7)
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]

    # Pasto: verde anime uniforme (dos tonos para las franjas del corte de césped).
    pasto = (h > 33) & (h < 85) & (s > 70) & (v > 85)
    # Pelo y sombras de cuerpo: oscuros que la transmisión tiñe de verde -> marrón casi negro.
    pelo = ~pasto & (h > 25) & (h < 60) & (v <= 85)
    h = np.where(pelo, 8, h)
    s = np.where(pelo, s * 0.45, s)
    # Piel: la transmisión la tiñe de oliva con el reflejo del pasto; se la lleva a un tono piel de dibujo.
    piel = ~pasto & ~pelo & (h > 4) & (h < 33) & (s > 35) & (v > 70)
    h = np.where(piel, 11 + (h - 11) * 0.2, h)
    s = np.where(piel, np.clip(s * 0.9 + 25, 0, 200), s)
    # Camisetas azules / cielo: azul saturado de dibujo.
    azul = (h > 95) & (h < 130) & (s > 45)
    s = np.where(pasto, np.clip(s * 1.5 + 30, 0, 255), np.clip(s * 1.35 + 10, 0, 255))
    h = np.where(pasto, 52 + (h - 52) * 0.3, h)
    h = np.where(azul, 108 + (h - 108) * 0.4, h)

    # Franjas del césped: dos verdes según el brillo local (corte de pasto en dos tonos, como en los dibujos).
    vb = cv2.GaussianBlur(v, (0, 0), 14)
    vm = cv2.GaussianBlur(v, (0, 0), 60)
    v = np.where(pasto, np.clip(172 + (vb - vm) * 1.6 + (v - vb) * 0.3, 120, 225), v)
    # Luces y sombras en escalones (cel shading): 4 niveles con borde suave.
    niv = 4
    q = v / 255.0 * niv
    frac = q - np.floor(q)
    paso = np.floor(q) + np.clip((frac - 0.5) * 6 + 0.5, 0, 1)
    v = np.where(pasto, v, np.clip(paso / niv * 255 * 1.05 + 18, 0, 255))
    # Blancos de camiseta: limpios, con un leve tono celeste en sombra (papel de cel).
    blanco = (s < 45) & (v > 150)
    v = np.where(blanco, np.maximum(v, 235), v)
    s = np.where(blanco, s * 0.5, s)

    hsv = np.stack([h, s, v], -1).clip(0, 255).astype(np.uint8)
    color = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

    # Líneas de cal: lo blanco y fino del original (top-hat) se pinta blanco, sin tinta encima.
    hs0 = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    g0 = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    th = cv2.morphologyEx(g0, cv2.MORPH_TOPHAT, np.ones((9, 9), np.uint8))
    cal = ((th > 28) & (hs0[..., 1] < 90)).astype(np.uint8)
    cerca_pasto = cv2.dilate(pasto.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    cal = cv2.morphologyEx(cal, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8)) * cerca_pasto
    cal = cv2.dilate(cal, np.ones((2, 2), np.uint8)).astype(bool)
    color[cal] = (240, 245, 235)

    # Tinta: bordes de luminancia (umbral adaptativo) + contornos de Canny, sin el ruido del pasto.
    gris = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    gris = cv2.medianBlur(gris, 5)
    adapt = cv2.adaptiveThreshold(gris, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 9, 8)
    canny = cv2.Canny(cv2.GaussianBlur(img, (0, 0), 1.2), 60, 140)
    tinta = cv2.max(adapt, canny)
    # Fuera los puntitos sueltos (el pasto los genera de a montones).
    n, lab, st, _ = cv2.connectedComponentsWithStats(tinta, 8)
    chicos = st[:, cv2.CC_STAT_AREA] < 24
    chicos[0] = False
    tinta[chicos[lab]] = 0
    tinta[cv2.dilate(cal.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0] = 0
    tinta = cv2.dilate(tinta, np.ones((2, 2), np.uint8))
    return color, tinta


# ---------------------------------------------------------------- suciedad analógica
class Cinta:
    def __init__(self, seed, sucio):
        self.rng = np.random.default_rng(seed)
        self.s = sucio
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        self.vin = np.clip(1.15 - 0.42 * r ** 2.2, 0.35, 1)[..., None]
        self.scan = np.where((np.arange(H) % 3) == 0, 0.86, 1.0).astype(np.float32)[:, None, None]
        # Textura de papel/cel fija (manchas de baja frecuencia).
        p = cv2.GaussianBlur(self.rng.standard_normal((H // 4, W // 4)).astype(np.float32), (0, 0), 6)
        self.papel = cv2.resize(p / (np.abs(p).max() + 1e-6), (W, H))[..., None]
        self.tracking_y = None
        self.rayas = []  # (x, vida)

    def aplicar(self, img, k):
        rng, s = self.rng, self.s
        f = img.astype(np.float32)
        if s <= 0:
            return np.clip(f, 0, 255).astype(np.uint8)
        # Papel + desvaído (negros levantados, tinte cálido de cinta vieja).
        f = f * (1 + 0.05 * s * self.papel)
        f = f * (1 - 0.10 * s) + np.array([20, 12, 18], np.float32) * s

        # Color corrido: croma de baja resolución, desplazado a la derecha (sangrado VHS).
        ycc = cv2.cvtColor(np.clip(f, 0, 255).astype(np.uint8), cv2.COLOR_RGB2YCrCb).astype(np.float32)
        cr = cv2.resize(cv2.resize(ycc[..., 1], (W // 6, H // 2)), (W, H))
        cb = cv2.resize(cv2.resize(ycc[..., 2], (W // 6, H // 2)), (W, H))
        d = int(6 * s)
        ycc[..., 1] = np.roll(cr, d, 1)
        ycc[..., 2] = np.roll(cb, d + 2, 1)
        # Luma un poco blanda + realce (el "sharpen" barato de las caseteras).
        y = ycc[..., 0]
        bl = cv2.GaussianBlur(y, (0, 0), 1.3)
        ycc[..., 0] = bl + (y - cv2.GaussianBlur(y, (0, 0), 3)) * 0.6
        f = cv2.cvtColor(np.clip(ycc, 0, 255).astype(np.uint8), cv2.COLOR_YCrCb2RGB).astype(np.float32)

        # Aberración: rojo y azul apenas corridos.
        f[..., 0] = np.roll(f[..., 0], int(2 * s), 1)
        f[..., 2] = np.roll(f[..., 2], -int(2 * s), 1)

        # Ondulación horizontal de línea (jitter de cinta): seno lento + ruido por fila.
        fase = k * 0.21
        off = (np.sin(np.arange(H) / 37.0 + fase) * 1.5 + rng.standard_normal(H) * 0.6) * s
        # Barra de tracking: aparece de vez en cuando y baja por la pantalla.
        if self.tracking_y is None and rng.random() < 0.025 * s:
            self.tracking_y = -60.0
        ruido_banda = None
        if self.tracking_y is not None:
            self.tracking_y += 38
            yb = int(self.tracking_y)
            a, b = max(0, yb), min(H, yb + 50)
            if a < b:
                off[a:b] += rng.standard_normal(b - a) * 14 * s + 18 * s
                ruido_banda = (a, b)
            if yb > H:
                self.tracking_y = None
        # Head switching: abajo de todo, filas corridas.
        off[H - 14:] += 22 * s + rng.standard_normal(14) * 8
        # Corte roto: cada tanto un bloque de líneas salta fuerte.
        if rng.random() < 0.035 * s:
            y0 = int(rng.integers(0, H - 120))
            off[y0:y0 + int(rng.integers(8, 120))] += rng.choice([-1, 1]) * rng.uniform(30, 120)
        f = self._correr_filas(f, off)
        if ruido_banda:
            a, b = ruido_banda
            nb = rng.random((b - a, W)) ** 6 * 255
            f[a:b] = f[a:b] * 0.7 + nb[..., None] * 0.6
        f[H - 14:] = f[H - 14:] * 0.6 + rng.random((14, W, 1)) * 90

        # Grano grueso (generado a media resolución).
        g = rng.standard_normal((H // 2, W // 2)).astype(np.float32)
        g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
        f = f + g * 11 * s

        # Polvo y pelos (manchas blancas y negras de un cuadro) + rayas verticales que duran varios cuadros.
        for _ in range(rng.poisson(5 * s)):
            x, yy = int(rng.integers(0, W)), int(rng.integers(0, H))
            r = int(rng.integers(1, 5))
            col = 255 if rng.random() < 0.6 else 10
            cv2.circle(f, (x, yy), r, (col, col, col), -1, cv2.LINE_AA)
        if rng.random() < 0.05 * s:
            self.rayas.append([int(rng.integers(0, W)), int(rng.integers(6, 30))])
        for r_ in self.rayas:
            x = r_[0] + int(rng.integers(-2, 3))
            r_[0] = x
            cv2.line(f, (x, 0), (x + int(rng.integers(-6, 7)), H), (225, 225, 215), 1, cv2.LINE_AA)
            r_[1] -= 1
        self.rayas = [r_ for r_ in self.rayas if r_[1] > 0]

        f = f * self.scan * self.vin
        # Parpadeo de brillo.
        f = f * (1 + rng.standard_normal() * 0.025 * s)
        return np.clip(f, 0, 255).astype(np.uint8)

    @staticmethod
    def _correr_filas(f, off):
        """Desplaza cada fila horizontalmente off[y] píxeles (con repetición del borde)."""
        xs = np.arange(W, dtype=np.float32)[None, :] - off[:, None].astype(np.float32)
        ys = np.repeat(np.arange(H, dtype=np.float32)[:, None], W, 1)
        return cv2.remap(f, xs, ys, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def main():
    pos, op = args()
    video, desde, dur, salida = pos[0], float(pos[1]), float(pos[2]), pos[3]
    vel, tiempos, sucio = float(op["vel"]), int(op["tiempos"]), float(op["suciedad"])
    rng = np.random.default_rng(int(op["semilla"]))
    cinta = Cinta(int(op["semilla"]), sucio)

    fuente_dur = dur * vel
    vf = f"scale={TW}:{TH},setpts=PTS/{vel}" if vel != 1 else f"scale={TW}:{TH}"
    lee = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(desde), "-t", str(fuente_dur), "-i", video,
                            "-vf", vf + f",fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    esc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "17", "-preset", "medium",
                            "-pix_fmt", "yuv420p", "-an", salida], stdin=subprocess.PIPE)
    tam = TW * TH * 3
    k, dibujo, salto = 0, None, (0, 0)
    tinta_col = np.array([28, 22, 40], np.float32)
    while True:
        buf = lee.stdout.read(tam)
        if len(buf) < tam:
            break
        if k % tiempos == 0:
            fr = np.frombuffer(buf, np.uint8).reshape(TH, TW, 3)
            color, tinta = cel(fr)
            color = cv2.resize(color, (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32)
            t = cv2.resize(tinta, (W, H), interpolation=cv2.INTER_LINEAR)
            t = cv2.GaussianBlur(t, (0, 0), 0.8).astype(np.float32)[..., None] / 255
            dibujo = color * (1 - t) + tinta_col * t
            # "Gate weave": cada dibujo queda un pelín corrido, como cels mal registrados en la cámara.
            salto = (rng.normal(0, 2.2 * sucio), rng.normal(0, 1.6 * sucio))
        M = np.float32([[1, 0, salto[0]], [0, 1, salto[1]]])
        cuadro = cv2.warpAffine(dibujo, M, (W, H), borderMode=cv2.BORDER_REFLECT)
        esc.stdin.write(cinta.aplicar(cuadro, k).tobytes())
        k += 1
        if k % 30 == 0:
            print(f"  {k / FPS:.0f}s", flush=True)
    esc.stdin.close()
    esc.wait()
    print("listo:", salida)


if __name__ == "__main__":
    main()
