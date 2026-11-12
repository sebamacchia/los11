"""Subtítulos en inglés para YouTube (segunda pista) a partir del .srt en español que genera armar.py.

Uso: python3 herramientas/subtitulos_en.py proyectos/<p> guion_c.json guion_c_en.json
  -> salida/subtitulos_guion_c_en.srt

guion_c_en.json = lista con la traducción de cada escena, en el mismo orden (cadena vacía en las escenas sin texto).
Cada cue del .srt español se asigna a su escena (por el texto); las frases inglesas de la escena se reparten
entre esos cues en proporción a su largo, cortando por oraciones."""
import json
import re
import sys
from pathlib import Path


def leer_srt(ruta):
    cues = []
    for bloque in re.split(r"\n\s*\n", Path(ruta).read_text().strip()):
        lineas = bloque.strip().split("\n")
        if len(lineas) >= 3:
            cues.append((lineas[1], " ".join(lineas[2:]).strip()))
    return cues


def oraciones(txt):
    return [o for o in re.split(r"(?<=[.!?…])\s+", txt.strip()) if o]


def repartir(frases, k):
    """Reparte las oraciones en k grupos consecutivos con largos parecidos."""
    if k <= 1 or not frases:
        return [" ".join(frases)] + [""] * (k - 1)
    total = sum(len(f) for f in frases)
    grupos, actual, acum = [], [], 0
    for f in frases:
        actual.append(f)
        acum += len(f)
        if len(grupos) < k - 1 and acum >= total * (len(grupos) + 1) / k - len(f) / 2:
            grupos.append(" ".join(actual))
            actual = []
    grupos.append(" ".join(actual))
    while len(grupos) < k:
        grupos.append("")
    return grupos


def main(proyecto, guion, traduccion):
    proyecto = Path(proyecto)
    g = json.load(open(proyecto / guion))
    en = json.load(open(proyecto / traduccion))
    escenas = g["escenas"]
    assert len(en) == len(escenas), f"{len(en)} traducciones para {len(escenas)} escenas"
    nombre = Path(guion).stem
    cues = leer_srt(proyecto / "salida" / f"subtitulos_{nombre}.srt")
    # cue -> escena: recorre las escenas en orden, buscando el texto del cue dentro de cada una
    asignacion, i = [], 0
    for _, txt in cues:
        while i < len(escenas) and txt not in escenas[i].get("texto", ""):
            i += 1
        if i >= len(escenas):
            raise SystemExit(f"No encuentro la escena del cue: {txt!r}")
        asignacion.append(i)
    salida, n = [], 1
    for esc_i in sorted(set(asignacion)):
        idx = [k for k, a in enumerate(asignacion) if a == esc_i]
        textos = repartir(oraciones(en[esc_i]), len(idx))
        for k, t in zip(idx, textos):
            if t:
                salida.append(f"{n}\n{cues[k][0]}\n{t}\n")
                n += 1
    dest = proyecto / "salida" / f"subtitulos_{nombre}_en.srt"
    dest.write_text("\n".join(salida))
    print(f"{dest}: {n - 1} cues")


if __name__ == "__main__":
    main(*sys.argv[1:4])
