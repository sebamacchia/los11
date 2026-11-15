"""Pasa un guion.json a un .docx para trabajarlo en Google Docs (capítulos, escenas con minuto estimado, texto del
narrador y qué se ve). El .json sigue siendo la fuente de verdad: lo que se edite en el doc se pasa a mano al guion.

  herramientas/.venv/bin/python herramientas/guion_docx.py proyectos/<p>/guion_x.json <salida.docx> \
      [--titulo "Argentina 1986"] [--version j] [--cambios cambios.txt]

Duración estimada: ~2,45 palabras por segundo de narración (medido en la versión g) + pausas + escenas mudas.
"""
import json
import sys
from datetime import date
from pathlib import Path

from docx import Document
from docx.shared import Pt, RGBColor

PALABRAS_SEG = 2.45
GRIS = RGBColor(0x6B, 0x6B, 0x6B)


def args():
    a = sys.argv[1:]
    op, pos, i = {}, [], 0
    while i < len(a):
        if a[i].startswith("--"):
            op[a[i][2:]] = a[i + 1]
            i += 2
        else:
            pos.append(a[i])
            i += 1
    return pos, op


def mmss(s):
    s = int(round(s))
    return f"{s // 60}:{s % 60:02}"


def nombre(archivo):
    return Path(archivo).name


def describir_visual(v):
    t = v.get("tipo")
    if t is None and "archivo" in v:
        d = f"{nombre(v['archivo'])} desde {v.get('desde', v.get('gol', 0))}s"
        if v.get("velocidad", 1) != 1:
            d += f" (cámara lenta x{v['velocidad']})"
        if v.get("golpe"):
            d += f" · marcador {v['golpe']}"
        if v.get("zocalo"):
            d += f" · zócalo {v['zocalo']}"
        return d
    if t == "doc":
        partes = []
        for pl in v.get("planos", []):
            fotos = [nombre(c["archivo"]) for c in pl.get("capas", [])]
            textos = [r["texto"].replace("\n", " ") for r in pl.get("rotulos", [])
                      if r.get("tipo") in ("titulo", "maquina") and r.get("texto")]
            mesa = pl.get("mesa")
            base = " + ".join(fotos) if fotos else ("fondo de " + nombre(mesa["archivo"]) if isinstance(mesa, dict)
                                                    else "fondo negro" if mesa == "negro" else "papel")
            if textos:
                base += " · textos: " + " / ".join(f"«{x}»" for x in textos[:4])
            partes.append(base)
        return "doc: " + " ⟶ ".join(partes)
    if t == "capitulo":
        return f"separador de capítulo {v.get('numero')}: {v.get('titulo')}"
    if t == "intro":
        return "intro animada del canal"
    if t == "cierre":
        return "pantalla final (suscribite / like / comentá)"
    return t or "?"


def describir_mudo(e):
    for s in e.get("sfx", []):
        if "archivo" in s:
            a = nombre(s["archivo"])
            if "vh_" in a:
                return "Sin narrador: relato original de Víctor Hugo Morales"
            if "llamada" in a:
                return "Sin narrador: audio original de la llamada (solo Diego y Doña Tota)"
            return f"Sin narrador: audio original ({a})"
    return "Sin narrador: música y ambiente"


def main():
    pos, op = args()
    g = json.loads(Path(pos[0]).read_text())
    E = g["escenas"]
    version = op.get("version", "?")
    doc = Document()
    doc.styles["Normal"].font.name = "Arial"
    doc.styles["Normal"].font.size = Pt(11)

    t = 0.0
    filas = []
    for e in E:
        vis = e.get("visual", [])
        vis = vis if isinstance(vis, list) else [vis]
        tipos = {v.get("tipo") for v in vis}
        if e.get("texto"):
            d = len(e["texto"].split()) / PALABRAS_SEG + e.get("pausa", g.get("pausa", 0.45)) + e.get("retardo", 0)
        elif "capitulo" in tipos:
            d = 2.5
        elif "intro" in tipos:
            d = 3.0
        else:
            d = e.get("duracion", 5)
        filas.append((t, e, vis, tipos))
        t += d
    total = t

    doc.add_heading(op.get("titulo", g.get("archivo", "Guion")), 0)
    doc.add_paragraph(f"Guion — versión {version} del {date.today():%d/%m/%Y}. Fuente de verdad: "
                      f"{Path(pos[0]).name} (las ediciones de acá se pasan a mano al guion). "
                      f"Duración estimada: {mmss(total)} ({len(E)} escenas).")
    if op.get("cambios"):
        doc.add_heading("Cambios de esta versión", 1)
        for linea in Path(op["cambios"]).read_text().strip().splitlines():
            doc.add_paragraph(linea.lstrip("-• ").strip(), style="List Bullet")

    n = 0
    for t0, e, vis, tipos in filas:
        n += 1
        if "capitulo" in tipos:
            c = next(v for v in vis if v.get("tipo") == "capitulo")
            doc.add_heading(f"Capítulo {c.get('numero')}: {c.get('titulo')} ({mmss(t0)})", 1)
            continue
        if "intro" in tipos:
            doc.add_paragraph(f"{n}. [{mmss(t0)}] Intro animada del canal")
            continue
        if e.get("capitulo") and n == 1:
            doc.add_heading(e["capitulo"], 1)
        doc.add_heading(f"{n}. [{mmss(t0)}]", 3)
        p = doc.add_paragraph()
        if e.get("texto"):
            p.add_run(e["texto"])
        else:
            r = p.add_run(f"({describir_mudo(e)})")
            r.italic = True
        im = doc.add_paragraph(style="List Bullet")
        r = im.add_run("Imagen: " + " → ".join(describir_visual(v) for v in vis))
        r.font.size = Pt(9)
        r.font.color.rgb = GRIS
    doc.save(pos[1])
    print(f"{pos[1]}: {len(E)} escenas, {mmss(total)} estimados")


if __name__ == "__main__":
    main()
