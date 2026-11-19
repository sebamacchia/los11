"""Marcos para fotos y clips del estilo carpeta (18/11, pedido del usuario: "cambiemos a veces el recorte de papel,
algo similar pero otra cosa, sino es muy repetitivo"). Uno por capítulo, junto con su papel de fondo (TEMAS en
carpeta_doc.py). Todos tienen la misma firma que carpeta.recorte_cuadro(im, seed) y devuelven RGBA con sombra.

  tijera      el de siempre (carpeta.recorte_cuadro): bordes rectos mellados
  cinta       tijera + dos tiras de cinta adhesiva en las esquinas de arriba
  laboratorio copia de laboratorio: borde blanco, más ancho abajo
  dentado     tijera de picos (zigzag)
  esquineros  esquineros negros de álbum de fotos
"""
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PAD = 40


def _sombra(img, seed, off=(6, 9), blur=7, op=0.5):
    out = Image.new("RGBA", (img.width + 2 * PAD, img.height + 2 * PAD), (0, 0, 0, 0))
    s = Image.new("RGBA", img.size, (10, 6, 2, 255))
    s.putalpha(img.split()[3].point(lambda v: v * op))
    capa = Image.new("RGBA", out.size, (0, 0, 0, 0))
    capa.alpha_composite(s, (PAD + off[0], PAD + off[1]))
    out.alpha_composite(capa.filter(ImageFilter.GaussianBlur(blur)))
    out.alpha_composite(img, (PAD, PAD))
    return out


def cinta(im, seed=2, **kw):
    import carpeta as C
    base = C._recorte_tijera(im, seed=seed)
    out = Image.new("RGBA", (base.width + 2 * PAD, base.height + 2 * PAD), (0, 0, 0, 0))
    out.alpha_composite(base, (PAD, PAD))
    rng = np.random.default_rng(seed)
    largo = int(min(220, max(110, base.width * 0.28)))
    alto = int(largo * 0.29)
    for k, (x, y) in enumerate(((PAD + 10, PAD + 14), (PAD + base.width - largo - 10, PAD + 14))):
        t = np.zeros((alto, largo, 4), "uint8")
        t[..., :3] = (238, 232, 205)
        t[..., 3] = np.clip(165 + rng.normal(0, 12, (alto, largo)), 120, 200)
        tira = Image.fromarray(t)
        m = Image.new("L", tira.size, 0)
        z = max(4, alto // 10)
        pts = [(0, 0), (largo, 0)] + [(largo - (z if j % 2 else 0), alto * j / 4) for j in range(1, 5)] + \
              [(0, alto)] + [((z if j % 2 else 0), alto * (4 - j) / 4) for j in range(1, 4)]
        ImageDraw.Draw(m).polygon(pts, fill=255)
        tira.putalpha(Image.fromarray(np.minimum(np.asarray(tira.split()[3]), np.asarray(m))))
        tira = tira.rotate((35 if k == 0 else -30) + rng.uniform(-6, 6), expand=True, resample=Image.BICUBIC)
        out.alpha_composite(tira, (int(x - tira.width * 0.35), int(y - tira.height * 0.55)))
    return out


def laboratorio(im, seed=2, **kw):
    w, h = im.size
    b = max(8, int(min(w, h) * 0.03))
    papel = Image.new("RGBA", (w + 2 * b, h + 2 * b + int(b * 2.2)), (250, 248, 242, 255))
    papel.paste(im.convert("RGB"), (b, b))
    return _sombra(papel, seed)


def dentado(im, seed=2, **kw):
    p = im.convert("RGBA")
    w, h = p.size
    z = max(6, int(min(w, h) * 0.014))
    pts = []
    for x in range(0, w + 1, 2 * z):
        pts += [(x, 0), (x + z, z)]
    for y in range(0, h + 1, 2 * z):
        pts += [(w, y), (w - z, y + z)]
    for x in range(w, -1, -2 * z):
        pts += [(x, h), (x - z, h - z)]
    for y in range(h, -1, -2 * z):
        pts += [(0, y), (z, y - z)]
    m = Image.new("L", p.size, 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    p.putalpha(m)
    return _sombra(p, seed, blur=5, op=0.6)


def esquineros(im, seed=2, **kw):
    p = im.convert("RGBA")
    w, h = p.size
    s = max(26, int(min(w, h) * 0.09))
    d = ImageDraw.Draw(p)
    for a, b, c in (((0, 0), (s, 0), (0, s)), ((w, 0), (w - s, 0), (w, s)), ((0, h), (s, h), (0, h - s)),
                    ((w, h), (w - s, h), (w, h - s))):
        d.polygon([a, b, c], fill=(22, 20, 18, 255))
    return _sombra(p, seed)


MARCOS = {"cinta": cinta, "laboratorio": laboratorio, "dentado": dentado, "esquineros": esquineros}
