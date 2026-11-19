"""Rehacer UNA pieza de Argentina 86 y actualizar el Vibe Editor (17/11, pedido del usuario: "cuando hago un cambio,
cambia solo eso en el vibe editor"). Renderiza solo esa pieza, re-mezcla su capítulo (el video se pega sin
re-codificar: segundos) y reescribe el manifiesto; la página se recarga sola en el mismo segundo.

  herramientas/.venv/bin/python proyectos/argentina-1986/rehacer.py p4_2 [p4_3 ...] [--capas] [--capas-solo pesa,tonelada]
    --capas        también rehace las capas ProRes de FilmCraft (lento)
    --capas-solo   rehace solo esas capas (FilmCraft) además del video
Si cambia la última pieza de un capítulo, también rehace la placa del capítulo siguiente (arranca sobre ese cuadro).
"""
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "herramientas"))
import carpeta as C  # noqa: E402
import carpeta_doc as D  # noqa: E402

G = AQUI / "salida" / "graficos"
LISTAS = {"p2": (D.ESCENAS, "2"), "p3": (D.CAPITULO2, "3"), "p4": (D.CAPITULO3, "4"), "p5": (D.CAPITULO4, "5"),
         "p6": (D.CAPITULO5, "6"), "p7": (D.CAPITULO6, "7"), "p8": (D.CAPITULO7, "8"), "p9": (D.CAPITULO8, "9"),
         "p10": (D.CAPITULO9, "10")}
PLACAS = {"capitulo1_1986": ("1", "Nadie creía", "intro_cierre_f.mp4", "2"),
          "capitulo2_1986": ("2", "El grupo", "p2_7.mp4", "3"),
          "capitulo3_1986": ("3", "Las camisetas", "p3_4.mp4", "4"),
          "capitulo4_1986": ("4", "La guerra", "p4_4.mp4", "5"),
          "capitulo5_1986": ("5", "La mano de Dios", "p5_5.mp4", "6"),
          "capitulo6_1986": ("6", "El gol del siglo", "p6_5.mp4", "7"),
          "capitulo7_1986": ("7", "Bélgica", "p7_9.mp4", "8"),
          "capitulo8_1986": ("8", "La final", "p8_3.mp4", "9"),
          "capitulo9_1986": ("9", "El Mundial de Diego", "p9_10.mp4", "10")}


def rehacer(pieza, capas=False, capas_solo=None):
    """Devuelve la parte (corte) que hay que re-mezclar y las piezas extra que dependen de esta."""
    t = time.time()
    if pieza in PLACAS:
        n, tit, antes, parte = PLACAS[pieza]
        C.capitulo_1986(n, tit, str(G / f"{pieza}.mp4"), capas=capas, antes=antes)
        extra = []
    else:
        pre, k = pieza.split("_")
        lista, parte = LISTAS[pre]
        s, cam = lista[int(k) - 1]()
        s.render(capas=capas, camara=cam)
        if capas_solo:
            s.render(capas=True, solo=set(capas_solo), camara=cam)
        extra = [p for p, (_, _, antes, _) in PLACAS.items() if antes == f"{pieza}.mp4"]
    print(f"  {pieza}: {time.time() - t:.0f} s")
    return parte, extra


def main():
    a = sys.argv[1:]
    capas = "--capas" in a
    solo = a[a.index("--capas-solo") + 1].split(",") if "--capas-solo" in a else None
    piezas = [x for x in a if not x.startswith("--") and (not solo or x != ",".join(solo))]
    partes = []
    while piezas:
        parte, extra = rehacer(piezas.pop(0), capas, solo)
        partes.append(parte)
        piezas += [e for e in extra if e not in piezas]
    for parte in dict.fromkeys(partes):
        t = time.time()
        subprocess.run([sys.executable, str(AQUI / "mezcla_parte2.py"), "--parte", parte, "--stems"], check=True,
                       capture_output=True)
        print(f"  parte{parte} mezclada: {time.time() - t:.0f} s → el Vibe Editor se actualiza solo")


if __name__ == "__main__":
    main()
