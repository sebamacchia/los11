"""Buscador de imágenes "tipo Google": busca en toda la web (DuckDuckGo Imágenes, sin clave), baja las
candidatas, arma una hoja de contacto y marca de qué tipo de fuente viene cada una (derechos).

    herramientas/.venv/bin/python herramientas/imagenes.py buscar proyectos/<p> "Hernan Crespo Milan 2005" [n=40] [--min 800]
    herramientas/.venv/bin/python herramientas/imagenes.py elegir proyectos/<p> crespo-milan-2005 07=crespo_festejo 12=crespo_cabeza

- `buscar` deja todo en <proyecto>/material/candidatas/<búsqueda>/ (NN.jpg + fuentes.json + hoja.jpg).
- `elegir` copia las elegidas a <proyecto>/material/ y anota en creditos.txt de dónde salió cada una.

Tipos de fuente (van en la hoja de contacto, con color):
  AGENCIA  Getty, Alamy, Shutterstock, AP, Reuters, AFP, EFE...: la vista previa trae marca de agua.
           Para usarla en el canal hay que comprar la licencia editorial (o buscar otra).
  PRENSA   diarios y sitios de fútbol: la foto es de ellos o de una agencia. Riesgo de reclamo.
  LIBRE    Wikimedia Commons / Flickr con Creative Commons: se usa con crédito.
  OTRA     Pinterest, foros, blogs: origen desconocido.
El canal decide qué riesgo toma; la herramienta solo lo deja a la vista.
(Usar el python del entorno: herramientas/.venv tiene ddgs y Pillow.)
"""
import json
import re
import shutil
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/128.0 Safari/537.36"}
AGENCIAS = ("gettyimages", "alamy", "shutterstock", "apimages", "reuters", "afp", "efe.com", "imago-images",
            "dreamstime", "istockphoto", "depositphotos", "123rf", "offside", "sportsphoto", "pa images",
            "panoramic", "lapresse", "photoshot")
LIBRES = ("wikimedia", "wikipedia", "flickr.com")
OTRAS = ("pinterest", "pinimg", "reddit", "tumblr", "facebook", "instagram", "x.com", "twitter")
COLOR = {"AGENCIA": (200, 16, 46), "PRENSA": (232, 179, 58), "LIBRE": (122, 179, 122), "OTRA": (150, 150, 150)}


def tipo(r):
    txt = " ".join(str(r.get(k, "")) for k in ("source", "url", "image")).lower()
    if any(a in txt for a in AGENCIAS):
        return "AGENCIA"
    if any(a in txt for a in LIBRES):
        return "LIBRE"
    if any(a in txt for a in OTRAS):
        return "OTRA"
    return "PRENSA"


def slug(s):
    s = s.lower()
    for a, b in zip("áéíóúñü", "aeiounu"):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:60]


def _bajar(r):
    for url in (r.get("image"), r.get("thumbnail")):
        if not url:
            continue
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25) as f:
                im = Image.open(BytesIO(f.read()))
                im.load()
                return im.convert("RGB"), url
        except Exception:
            continue
    return None, None


def buscar(proyecto, consulta, n=40, minimo=0):
    from ddgs import DDGS
    res = DDGS().images(consulta, max_results=int(n) * 2)
    res = [r for r in res if min(int(r.get("width") or 0), int(r.get("height") or 0)) >= minimo][: int(n)]
    carpeta = Path(proyecto) / "material" / "candidatas" / slug(consulta)
    carpeta.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(8) as ex:
        bajadas = list(ex.map(_bajar, res))
    fichas = []
    for i, (r, (im, url)) in enumerate(zip(res, bajadas), 1):
        if im is None:
            continue
        nombre = f"{i:02d}.jpg"
        im.save(carpeta / nombre, quality=92)
        fichas.append({"n": f"{i:02d}", "archivo": nombre, "tipo": tipo(r), "ancho": im.width, "alto": im.height,
                       "titulo": r.get("title", ""), "pagina": r.get("url", ""), "imagen": url,
                       "fuente": r.get("source", "")})
    (carpeta / "fuentes.json").write_text(json.dumps(fichas, ensure_ascii=False, indent=1))
    hoja(carpeta, fichas, consulta)
    cuenta = {t: sum(f["tipo"] == t for f in fichas) for t in COLOR}
    print(f"{len(fichas)} imágenes en {carpeta}  ({', '.join(f'{k}: {v}' for k, v in cuenta.items() if v)})")
    print(f"hoja de contacto: {carpeta / 'hoja.jpg'}")


def hoja(carpeta, fichas, titulo, cols=6, w=320, h=240):
    filas = (len(fichas) + cols - 1) // cols
    S = Image.new("RGB", (cols * w, filas * (h + 34) + 50), (20, 22, 26))
    d = ImageDraw.Draw(S)
    try:
        fuente = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 15)
        grande = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 24)
    except OSError:
        fuente = grande = ImageFont.load_default()
    d.text((12, 12), f'"{titulo}"  —  rojo: agencia (licencia paga) · amarillo: prensa · verde: libre · gris: otra',
           fill=(230, 230, 230), font=grande)
    for i, f in enumerate(fichas):
        x, y = (i % cols) * w, 50 + (i // cols) * (h + 34)
        im = Image.open(carpeta / f["archivo"])
        im.thumbnail((w - 8, h - 8))
        S.paste(im, (x + (w - im.width) // 2, y + (h - im.height) // 2))
        d.rectangle([x + 4, y + h, x + w - 4, y + h + 28], fill=COLOR[f["tipo"]])
        d.text((x + 10, y + h + 5), f'{f["n"]} {f["tipo"]} {f["ancho"]}x{f["alto"]} {f["fuente"][:16]}',
               fill=(15, 15, 15), font=fuente)
    S.save(carpeta / "hoja.jpg", quality=88)


def elegir(proyecto, busqueda, *pares):
    carpeta = Path(proyecto) / "material" / "candidatas" / busqueda
    fichas = {f["n"]: f for f in json.loads((carpeta / "fuentes.json").read_text())}
    creditos = Path(proyecto) / "material" / "creditos.txt"
    with creditos.open("a") as c:
        for par in pares:
            n, nombre = par.split("=")
            f = fichas[n.zfill(2)]
            destino = Path(proyecto) / "material" / f"{nombre}.jpg"
            shutil.copy(carpeta / f["archivo"], destino)
            c.write(f'{destino.name}: {f["titulo"]} — {f["pagina"]} [{f["tipo"]}]\n')
            print(f"{destino}  [{f['tipo']}]")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        raise SystemExit(__doc__)
    if a[0] == "buscar":
        minimo = int(a[a.index("--min") + 1]) if "--min" in a else 0
        resto = [x for i, x in enumerate(a) if x != "--min" and (i == 0 or a[i - 1] != "--min")]
        buscar(resto[1], resto[2], *(resto[3:4]), minimo=minimo)
    elif a[0] == "elegir":
        elegir(*a[1:])
    else:
        raise SystemExit(__doc__)
