"""La mezcla final de la intro (mezcla_intro.py, versión 80s_a2) pasada a los .fcproj por capas (17/11).
Por cada pieza: <pieza>_capas/sonidos_mezcla/ con SOLO los efectos que quedaron en la mezcla (--mas-sfx), ya
procesados igual que en la mezcla (volumen x0.55, sin agudos, con sala), y el tramo de música de esa pieza (la pista
de música de la mezcla, ya agachada bajo la voz). Proyectos nuevos <pieza>_capas_mezcla.fcproj; los anteriores no se tocan.

  /usr/bin/python3 proyectos/argentina-1986/intro_filmcraft.py [--mezcla intro_1986_mezcla_80s_a2]
"""
import json
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(AQUI.parents[1] / "herramientas"))
import mezcla_intro as M  # noqa: E402
import filmcraft  # noqa: E402

K_SFX = 0.55
MAS = {"tiza", "carta", "madera_golpe", "caida_corta", "estatica"}


def main():
    a = sys.argv
    mezcla = a[a.index("--mezcla") + 1] if "--mezcla" in a else "intro_1986_mezcla_80s_a2"
    mus = M.G / f"{mezcla}_mus.wav"
    if not mus.exists():
        raise SystemExit(f"falta {mus.name}: correr mezcla_intro.py con --stems")
    quedan = M.QUEDAN | MAS
    # misma selección que la mezcla (separación 0.4 s sobre toda la intro)
    todos, t0, inicio = [], 0.0, {}
    for nombre, _ in M.PIEZAS:
        inicio[nombre] = t0
        for c in json.load(open(M.G / f"{nombre}.sonidos.json")):
            if Path(c["archivo"]).stem in quedan:
                todos.append(dict(c, pieza=nombre, global_en=t0 + c["en"]))
        t0 += M.dur(M.G / f"{nombre}.mp4")
    todos.sort(key=lambda c: c["global_en"])
    finos, ultimo = [], -9.0
    for c in todos:
        if c["global_en"] - ultimo >= 0.4:
            finos.append(c)
            ultimo = c["global_en"]
    for nombre, _ in M.PIEZAS:
        carpeta = M.G / f"{nombre}_capas"
        dest = carpeta / "sonidos_mezcla"
        dest.mkdir(exist_ok=True)
        fin, out = {}, []
        for n, q in enumerate(c for c in finos if c["pieza"] == nombre):
            nom = Path(q["archivo"]).stem
            f = f"sfx_{n:03d}_{nom}.wav"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(q["desde"]), "-t", str(q["dur"]), "-i", q["archivo"],
                            "-af", f"volume={q['vol'] * K_SFX:.3f},afade=t=out:st={max(0, q['dur'] - 0.3)}:d=0.3,"
                            "lowpass=f=6500,apad=pad_dur=0.2,aecho=0.8:0.6:35|70:0.18|0.1",
                            "-ar", "48000", "-ac", "2", str(dest / f)], check=True)
            d = M.dur(dest / f)
            lane = next(l for l in range(50) if fin.get(l, 0) <= q["en"])
            out.append({"id": f"sfx-{n:03d}", "file": f, "start": q["en"], "duration": round(d, 3), "label": nom,
                        "lane": lane, "source_file": q["archivo"]})
            fin[lane] = q["en"] + d
        json.dump(out, open(dest / "sfx_clips.json", "w"), indent=1)
        dp = M.dur(M.G / f"{nombre}.mp4")
        tramo = dest / "musica.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{inicio[nombre]:.3f}", "-t", f"{dp:.3f}", "-i", str(mus),
                        "-ar", "48000", "-ac", "2", str(tramo)], check=True)
        filmcraft.capas(carpeta, destino=M.G / f"{nombre}_capas_mezcla.fcproj", sonidos="sonidos_mezcla",
                        musica=tramo, forzar="--forzar" in a)
        print(f"  {nombre}: {len(out)} efectos + música {inicio[nombre]:.2f}-{inicio[nombre] + dp:.2f} s")


if __name__ == "__main__":
    main()
