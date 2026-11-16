"""Sonidos libres de Openverse (api.openverse.org: Freesound, Wikimedia, Jamendo...), sin clave.

Solo trae licencias que permiten uso comercial y modificación. Por defecto solo CC0 (no exige crédito);
con --by también CC BY / BY-SA (el crédito se anota igual en creditos.txt para la descripción).

  python3 herramientas/sonidos.py buscar "rubber stamp" [--by] [--max 3]     # lista con duración y licencia
  python3 herramientas/sonidos.py bajar <id> <proyecto> [nombre]              # a material/sonidos/<nombre>.mp3
"""
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
API = "https://api.openverse.org/v1/audio/"
UA = {"User-Agent": "los11-tools/1.0"}


def _get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return json.load(r)


def buscar(q, by=False, maximo=8, dur_max=None):
    """Resultados [{id, titulo, licencia, segundos, fuente, autor, url, pagina}], los más cortos primero."""
    p = {"q": q, "page_size": 20, "license_type": "commercial,modification"}
    if not by:
        p["license"] = "cc0"
    res = _get(API + "?" + urllib.parse.urlencode(p)).get("results", [])
    out = []
    for r in res:
        seg = (r.get("duration") or 0) / 1000
        if dur_max and seg > dur_max:
            continue
        out.append({"id": r["id"], "titulo": r["title"], "licencia": f"{r['license']} {r.get('license_version', '')}".strip(),
                    "segundos": round(seg, 1), "fuente": r["source"], "autor": r.get("creator") or "desconocido",
                    "url": r["url"], "pagina": r.get("foreign_landing_url", "")})
    return out[:maximo]


def bajar(id_, proyecto, nombre=None):
    r = _get(API + id_ + "/")
    carpeta = RAIZ / "proyectos" / proyecto / "material" / "sonidos"
    carpeta.mkdir(parents=True, exist_ok=True)
    ext = Path(urllib.parse.urlparse(r["url"]).path).suffix or ".mp3"
    nombre = nombre or re.sub(r"[^a-z0-9]+", "_", r["title"].lower()).strip("_")[:40]
    dest = carpeta / f"{nombre}{ext}"
    if not dest.exists():
        with urllib.request.urlopen(urllib.request.Request(r["url"], headers=UA), timeout=60) as resp:
            dest.write_bytes(resp.read())
    cred = RAIZ / "proyectos" / proyecto / "material" / "creditos.txt"
    linea = (f"sonidos/{dest.name}: \"{r['title']}\" — {r.get('creator') or 'desconocido'} — "
             f"{r['license'].upper()} {r.get('license_version', '')} — {r.get('foreign_landing_url', '')} (vía Openverse)")
    if cred.exists() and f"sonidos/{dest.name}:" in cred.read_text():
        return dest
    with open(cred, "a") as f:
        f.write(linea + "\n")
    return dest


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "buscar":
        mx = int(a[a.index("--max") + 1]) if "--max" in a else 8
        for r in buscar(a[1], by="--by" in a, maximo=mx):
            print(f"{r['id']}  {r['segundos']:>6}s  {r['licencia']:<10} {r['fuente']:<16} {r['titulo'][:50]}")
    elif a and a[0] == "bajar":
        print(bajar(a[1], a[2], a[3] if len(a) > 3 else None))
    else:
        print(__doc__)
