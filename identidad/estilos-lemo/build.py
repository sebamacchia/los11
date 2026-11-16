"""Arma index.html (catálogo de estilos de animación de LOS 11) juntando src/:
cabecera.html + base.js + ayudas.js + lote*.js + repro.js. Escribe identidad/estilos-lemo/index.html
y, si se pasa una ruta, una copia ahí (la que se publica como Artifact).
  /usr/bin/python3 identidad/estilos-lemo/build.py [copia.html]
"""
import json
import sys
from pathlib import Path

AQUI = Path(__file__).parent
S = AQUI / "src"
lotes = sorted(S.glob("lote*.js"))
js = "\n".join(p.read_text() for p in [S / "base.js", S / "ayudas.js", *lotes])
repro = (S / "repro.js").read_text().replace("/*CATS*/{}", (S / "categorias.json").read_text().strip())
html = (S / "cabecera.html").read_text() + "\n<script>\n" + js + "\n" + repro + "\n</script>\n"
(AQUI / "index.html").write_text('<meta charset="utf-8">\n' + html)  # charset solo para probar local (el Artifact ya lo trae)
if len(sys.argv) > 1:
    Path(sys.argv[1]).write_text(html)
n = js.count("ESTILOS.push(")
print(f"index.html: {n} estilos, {len(html) // 1024} KB ({', '.join(p.name for p in lotes)})")
