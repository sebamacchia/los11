"""Busca y baja fotos libres de Wikimedia Commons, guardando los créditos de licencia.

Buscar:  python3 herramientas/fotos.py buscar "Steven Gerrard" ["otra búsqueda" ...]
Bajar:   python3 herramientas/fotos.py bajar proyectos/<nombre>/material "File:Algo.jpg=gerrard" ...
Los créditos se agregan a <material>/creditos.txt (pegarlos en la descripción de YouTube).
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "LaHistoriaDelFutbol/1.0 (video research; contact via channel)"}


def _get(url, intentos=6):
    espera = 4
    for _ in range(intentos):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(espera)
            espera *= 2
    raise SystemExit("Wikimedia sigue limitando (429), probá en un rato")


def _api(**params):
    params["format"] = "json"
    return json.loads(_get(API + "?" + urllib.parse.urlencode(params)), strict=False)


def _limpio(html):
    return re.sub(r"<[^>]+>", "", html or "").strip()


def buscar(q, n=10):
    d = _api(action="query", generator="search", gsrsearch=q, gsrnamespace=6, gsrlimit=n,
             prop="imageinfo", iiprop="size|extmetadata")
    for p in sorted(d.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0)):
        ii = p["imageinfo"][0]
        m = ii.get("extmetadata", {})
        fecha = _limpio(m.get("DateTimeOriginal", {}).get("value", ""))[:10]
        lic = m.get("LicenseShortName", {}).get("value", "?")
        print(f"{p['title']}  [{ii['width']}x{ii['height']}] {lic} {fecha}")


def bajar(carpeta, pedidos, ancho=2400):
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    creditos = carpeta / "creditos.txt"
    for pedido in pedidos:
        titulo, _, nombre = pedido.partition("=")
        d = _api(action="query", titles=titulo, prop="imageinfo", iiprop="url|extmetadata", iiurlwidth=ancho)
        ii = list(d["query"]["pages"].values())[0]["imageinfo"][0]
        m = ii.get("extmetadata", {})
        url = ii.get("thumburl") or ii["url"]
        ext = Path(urllib.parse.urlparse(url).path).suffix.lower() or ".jpg"
        destino = carpeta / ((nombre or re.sub(r"\W+", "_", titulo[5:])[:40]) + ext)
        destino.write_bytes(_get(url))
        autor = _limpio(m.get("Artist", {}).get("value", "desconocido"))
        lic = m.get("LicenseShortName", {}).get("value", "?")
        with open(creditos, "a") as f:
            f.write(f"{destino.name}: \"{titulo[5:]}\" — {autor} — {lic} — "
                    f"https://commons.wikimedia.org/wiki/{urllib.parse.quote(titulo.replace(' ', '_'))}\n")
        print(f"ok {destino.name}  ({lic}, {autor[:40]})")
        time.sleep(1.5)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    if sys.argv[1] == "buscar":
        for q in sys.argv[2:]:
            print(f"== {q}")
            buscar(q)
            time.sleep(1.5)
    elif sys.argv[1] == "bajar":
        bajar(sys.argv[2], sys.argv[3:])
