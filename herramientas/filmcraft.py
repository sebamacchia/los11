"""Pasa un video armado por armar.py a un proyecto de FilmCraft, para editarlo a mano.

    python3 herramientas/filmcraft.py proyectos/<nombre>      (después de: armar.py proyectos/<nombre>)

Lo que queda en el proyecto (.fcproj en salida/):
  V1  cada pieza del video como un clip suelto (las fotos, videos, placas, marcador y zócalos
      ya vienen dibujados en cada pieza), uno detrás del otro, con su número de escena en el nombre
  A1  la voz del narrador, una frase por escena
  A2, A3 (y A5-A8 si se pisan muchos)  los efectos de sonido, sin que uno tape a otro
  A4  la música (repetida hasta cubrir su tramo)
  C1  los subtítulos (subtitulos.srt)
FilmCraft no hace el "ducking" que hace armar.py (bajar la música cuando habla el narrador): la música
entra más baja y se puede ajustar en la pista A4.

Piezas animadas por capas (carpeta.py --capas): python3 herramientas/filmcraft.py capas <salida>_capas
  -> una pista por elemento, voz y cada efecto suelto (ver capas()).

No pisa un .fcproj que ya existe (puede tener tus cambios): para rehacerlo, pasá --forzar.
"""
import json
import math
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CLI = RAIZ / "herramientas" / "filmcraft-cli" / "filmcraft-cli"


def _run(lineas, proyecto=None, guardar=None):
    """Corre comandos de FilmCraft (uno por línea) y devuelve el resultado de cada uno."""
    if not CLI.exists():
        raise SystemExit(f"No está la herramienta de FilmCraft en {CLI}")
    guion = Path(guardar).with_suffix(".jsonl")
    guion.write_text("".join(json.dumps(l, ensure_ascii=False) + "\n" for l in lineas))
    cmd = [str(CLI)] + (["--project", str(proyecto)] if proyecto else []) + ["run", str(guion)]
    if guardar:
        cmd += ["--save-as", str(guardar)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    guion.unlink()
    salida = [json.loads(l) for l in r.stdout.splitlines() if l.startswith("{")]
    malos = [s for s in salida if not s.get("ok")]
    if r.returncode or malos or len(salida) < len(lineas):
        raise SystemExit("FilmCraft falló:\n" + "\n".join(json.dumps(m, ensure_ascii=False) for m in malos)
                         + r.stderr[-2000:])
    return [s.get("result") for s in salida]


def _db(vol):
    return round(20 * math.log10(max(vol, 1e-4)), 2)


def _dur(archivo):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                        str(archivo)], capture_output=True, text=True)
    return float(r.stdout.strip())


def exportar(linea_json, destino, forzar=False):
    linea = json.loads(Path(linea_json).read_text())
    destino = Path(destino).resolve()
    if destino.exists() and not forzar:
        print(f"  {destino.name} ya existe (puede tener tus cambios): no lo toco. Usá --forzar para rehacerlo.")
        return destino

    medios = []
    for grupo in ("piezas", "voces", "efectos", "musica"):
        for x in linea[grupo]:
            if x["archivo"] not in medios:
                medios.append(x["archivo"])

    # 1) importar todo y crear la secuencia
    res = _run([{"id": "file.import", "params": {"paths": medios}},
                {"id": "file.newSequence", "params": {"name": destino.stem, "width": linea["ancho"],
                                                      "height": linea["alto"], "fps": linea["fps"],
                                                      "video": 1, "audio": 8}}], guardar=destino)
    if res[0]["errors"]:
        raise SystemExit(f"FilmCraft no pudo importar: {res[0]['errors']}")
    item = dict(zip(medios, res[0]["items"]))

    # 2) poner cada cosa en su pista
    pasos, ganancias = [], []

    def poner(archivo, pista, inicio, dur=None, video=True, ganancia=None):
        p = {"item": item[archivo], "track": pista, "seconds": round(inicio, 4), "insert": False}
        if video:
            p["audio"] = False
        else:
            p["video"] = False
        if dur is not None:
            p["duration"] = {"seconds": round(dur, 4)}
        pasos.append({"id": "timeline.place", "params": p})
        ganancias.append(ganancia)

    for x in linea["piezas"]:
        poner(x["archivo"], "V1", x["inicio"], x["duracion"])
    for x in linea["voces"]:
        poner(x["archivo"], "A1", x["inicio"], video=False)
    # efectos: la primera pista libre (A2, A3 y, si se pisan muchos, A5-A8); nunca uno encima de otro
    fin_pista = {k: -1.0 for k in ("A2", "A3", "A5", "A6", "A7", "A8")}
    for x in sorted(linea["efectos"], key=lambda e: e["inicio"]):
        d = _dur(x["archivo"])
        pista = next((k for k, f in fin_pista.items() if f <= x["inicio"]), min(fin_pista, key=fin_pista.get))
        fin_pista[pista] = x["inicio"] + d
        poner(x["archivo"], pista, x["inicio"], video=False, ganancia=_db(x["volumen"]))
    for x in linea["musica"]:
        d, t = _dur(x["archivo"]), 0.0
        while t < x["largo"] - 0.05:  # la pista se repite hasta cubrir su tramo
            poner(x["archivo"], "A4", x["inicio"] + t, min(d, x["largo"] - t), video=False,
                  ganancia=_db(x["volumen"] * 0.7))
            t += d
    for pista, nombre in (("V1", "Video"), ("A1", "Voz"), ("A2", "Efectos"), ("A3", "Efectos 2"), ("A4", "Música"),
                         ("A5", "Efectos 3"), ("A6", "Efectos 4"), ("A7", "Efectos 5"), ("A8", "Efectos 6")):
        pasos.append({"id": "timeline.setTrack", "params": {"track": pista, "name": nombre}})
        ganancias.append(None)
    if Path(linea["subtitulos"]).exists():
        pasos.append({"id": "captions.import", "params": {"path": linea["subtitulos"], "name": "Subtítulos",
                                                          "language": "es"}})
        ganancias.append(None)
        pasos.append({"id": "captions.setStyle", "params": {"track": "C1", "anchor": "bottom", "margin": 0.06,
                                                            "size": 34, "background": True}})
        ganancias.append(None)
    res = _run(pasos, proyecto=destino, guardar=destino)

    # 3) volumen de efectos y música, clip por clip
    vol = [{"id": "clip.audioGain", "params": {"clips": r["clips"], "mode": "set", "db": g}}
           for r, g in zip(res, ganancias) if g is not None and r and r.get("clips")]
    if vol:
        _run(vol, proyecto=destino, guardar=destino)
    print(f"  {len(linea['piezas'])} piezas de video, {len(linea['voces'])} frases, "
          f"{len(linea['efectos'])} efectos, música y subtítulos")
    return destino


def capas(carpeta, destino=None, forzar=False, sonidos="sonidos", musica=None):
    """Pieza animada por capas (carpeta.py --capas) -> .fcproj: V1 fondo, una pista de video por elemento (en el orden
    en que se apilan, cada clip arranca cuando entra), arriba el VHS; A1 la voz, A2... cada efecto como clip suelto
    (sonidos/sfx_clips.json de real-sfx). Para cambiar algo se rehace SOLO esa capa con el mismo nombre de archivo.
    `sonidos` = otra subcarpeta de efectos (p. ej. sonidos_mezcla, la selección de la mezcla final) y `musica` = un wav
    que va en su propia pista, abajo de todo, desde el segundo 0."""
    carpeta = Path(carpeta).resolve()
    d = json.loads((carpeta / "capas.json").read_text())
    destino = Path(destino or carpeta.with_suffix(".fcproj")).resolve()
    if destino.exists() and not forzar:
        print(f"  {destino.name} ya existe (puede tener tus cambios): no lo toco. Usá --forzar para rehacerlo.")
        return destino
    sfx_json = carpeta / sonidos / "sfx_clips.json"
    sfx = json.loads(sfx_json.read_text()) if sfx_json.exists() else []
    voces = d.get("voces") or ([d["voz"]] if d.get("voz") else [])
    videos = [carpeta / d["fondo"]] + [carpeta / c["archivo"] for c in d["capas"]] + \
             ([carpeta / d["vhs"]] if d.get("vhs") else [])
    audios = list(dict.fromkeys(v["archivo"] for v in voces)) + [str(carpeta / sonidos / x["file"]) for x in sfx] + \
        ([str(Path(musica).resolve())] if musica else [])
    medios = [str(v) for v in videos] + audios
    carriles = 1 + max([x["lane"] for x in sfx] or [0])
    res = _run([{"id": "file.import", "params": {"paths": medios}},
                {"id": "file.newSequence", "params": {"name": destino.stem, "width": 1920, "height": 1080,
                                                      "fps": d["fps"], "video": len(videos),
                                                      "audio": 1 + carriles + (1 if musica else 0)}}], guardar=destino)
    if res[0]["errors"]:
        raise SystemExit(f"FilmCraft no pudo importar: {res[0]['errors']}")
    item = dict(zip(medios, res[0]["items"]))
    pasos, nombres = [], []

    def poner(archivo, pista, inicio, dur=None, video=True, nombre=None):
        p = {"item": item[str(archivo)], "track": pista, "seconds": round(inicio, 4), "insert": False}
        p["audio" if video else "video"] = False
        if dur is not None:
            p["duration"] = {"seconds": round(dur, 4)}
        pasos.append({"id": "timeline.place", "params": p})
        nombres.append(nombre)

    poner(videos[0], "V1", 0, d["duracion"], nombre="fondo")
    for n, c in enumerate(d["capas"], 2):
        poner(carpeta / c["archivo"], f"V{n}", c["inicio"], nombre=c["nombre"])
    if d.get("vhs"):
        poner(carpeta / d["vhs"], f"V{len(videos)}", 0, nombre="vhs_play")
    for j, voz in enumerate(voces, 1):
        poner(voz["archivo"], "A1", voz["inicio"], video=False, nombre=f"voz {j}")
    for x in sfx:
        poner(carpeta / sonidos / x["file"], f"A{2 + x['lane']}", x["start"], video=False,
              nombre=f"{x['label']} ({Path(x['source_file']).stem})")
    pistas = [("V1", "fondo")] + [(f"V{n}", c["nombre"]) for n, c in enumerate(d["capas"], 2)] + \
             ([(f"V{len(videos)}", "vhs")] if d.get("vhs") else []) + [("A1", "Voz")] + \
             [(f"A{2 + i}", f"Efectos {i + 1}") for i in range(carriles)] + \
             ([(f"A{2 + carriles}", "Música")] if musica else [])
    if musica:
        poner(Path(musica).resolve(), f"A{2 + carriles}", 0, d["duracion"], video=False, nombre="música")
    for pista, nombre in pistas:
        pasos.append({"id": "timeline.setTrack", "params": {"track": pista, "name": nombre}})
        nombres.append(None)
    res = _run(pasos, proyecto=destino, guardar=destino)
    ren = [{"id": "clip.rename", "params": {"clips": r["clips"], "name": n}}
           for r, n in zip(res, nombres) if n and r and r.get("clips")]
    if ren:
        _run(ren, proyecto=destino, guardar=destino)
    print(f"  {destino.name}: {len(videos)} capas de video, voz y {len(sfx)} efectos sueltos")
    return destino


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    if sys.argv[1] == "capas":       # filmcraft.py capas <carpeta>_capas [--forzar]
        a = sys.argv     # [--sonidos sonidos_mezcla] [--musica x.wav] [--destino y.fcproj]
        op = {k: a[a.index("--" + k) + 1] for k in ("sonidos", "musica", "destino") if "--" + k in a}
        print(capas(a[2], forzar="--forzar" in a, **op))
        raise SystemExit
    proyecto = Path(sys.argv[1]).resolve()
    guion = json.loads((proyecto / "guion.json").read_text())
    print(exportar(proyecto / "tmp" / "linea.json",
                   proyecto / "salida" / (guion.get("archivo", proyecto.name) + ".fcproj"),
                   forzar="--forzar" in sys.argv))
