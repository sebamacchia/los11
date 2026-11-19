"""Mezcla final de la intro de Argentina 86 (17/11, pedido del usuario: "demasiado sonidito").
Una batería sola, estable, de base (musica/intro86_groove_a.mp3) que baja cuando habla el narrador; pocos efectos
(solo los golpes que marcan algo), bajos y "atrás" (sin agudos, con un poco de sala). Las piezas de video son las de
carpeta.py, ya renderizadas en mudo.

  /usr/bin/python3 proyectos/argentina-1986/mezcla_intro.py [--musica musica/otra.mp3] [--sfx 0.45] [--salida x.mp4] [--stems] [--mas-sfx] [--vol-musica 0.5] [--manifiesto]
  -> salida/graficos/intro_1986_mezcla.mp4 (+ intro_1986_mezcla_cues.json: qué efectos quedaron y cuándo)
"""
import json
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
G = AQUI / "salida" / "graficos"
EL = RAIZ / ".cache" / "elevenlabs"

PIEZAS = [  # (video mudo, voces [(mp3, en segundos dentro de la pieza)])
    ("intro_1986_c", [("voz_0b3fb10097956ca7", 1.4), ("voz_e9e33113512168db", 9.27), ("voz_65b28a80db8ec135", 15.61)]),  # VHS 1 s más corto (17/11)
    ("intro_1986_medio_a_v2", [("voz_73a6b0899b4b418f", 0.0)]),     # guion corto (17/11)
    ("intro_1986_medio_c_v2", [("voz_9d036defafe9497b", 0.0)]),     # texto corto (17/11)
    ("intro_cierre_f", [("voz_a48ef327b7e666e2", 0.3)]),
]
# efectos que se quedan (marcan algo); el resto (papelitos, plásticos, caídas de cada cosa) se va
QUEDAN = {"sello_thump", "libro_cae", "auto_pasa", "avion_pasa", "whoosh_grave", "whoosh_rapido", "vhs_entra"}
SEPARACION = 0.55      # dos efectos no pueden caer más juntos que esto


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True).stdout)


def main():
    a = sys.argv
    musica = RAIZ / (a[a.index("--musica") + 1] if "--musica" in a else "musica/intro86_groove_a.mp3")
    k_sfx = float(a[a.index("--sfx") + 1]) if "--sfx" in a else 0.45
    k_mus = float(a[a.index("--vol-musica") + 1]) if "--vol-musica" in a else 0.5
    quedan, sep = QUEDAN, SEPARACION
    if "--mas-sfx" in a:                     # 17/11: "agreguemos un poco de sound FX" (sin papelitos ni plásticos)
        quedan = QUEDAN | {"tiza", "carta", "madera_golpe", "caida_corta", "estatica"}
        sep = 0.4
    voces, cues, t0 = [], [], 0.0
    for nombre, vs in PIEZAS:
        for v, en in vs:
            voces.append((EL / f"{v}.mp3", t0 + en))
        for c in json.load(open(G / f"{nombre}.sonidos.json")):
            if Path(c["archivo"]).stem in quedan:
                cues.append(dict(c, en=round(t0 + c["en"], 3)))
        t0 += dur(G / f"{nombre}.mp4")
    total = t0
    cues.sort(key=lambda c: c["en"])
    finos, ultimo = [], -9.0
    for c in cues:
        if c["en"] - ultimo >= sep:
            finos.append(c)
            ultimo = c["en"]
    if "--mas-sfx" not in a:
        json.dump(finos, open(G / "intro_1986_mezcla_cues.json", "w"), indent=1)

    lista = G / ".concat_intro.txt"            # el video se pega sin re-codificar (como mezcla_parte2.py)
    lista.write_text("".join(f"file '{G / (nombre + '.mp4')}'\n" for nombre, _ in PIEZAS))
    ins = []
    n = 0
    fil = []
    # voz
    vz = []
    for j, (r, en) in enumerate(voces):
        ins += ["-i", str(r)]
        ms = int(en * 1000)
        fil.append(f"[{n + j}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[vz{j}]")
        vz.append(f"[vz{j}]")
    fil.append("".join(vz) + f"amix=inputs={len(vz)}:normalize=0:duration=longest,apad,atrim=0:{total:.3f},"
               "asplit=2[voz][voz_sc]")
    # efectos: bajos y atrás
    b = n + len(voces)
    ef = []
    for j, c in enumerate(finos):
        ins += ["-i", c["archivo"]]
        ms = int(c["en"] * 1000)
        fil.append(f"[{b + j}:a]aresample=48000,aformat=channel_layouts=stereo,atrim={c['desde']}:{c['desde'] + c['dur']},"
                   f"asetpts=PTS-STARTPTS,afade=t=out:st={max(0, c['dur'] - 0.3)}:d=0.3,volume={c['vol'] * k_sfx:.3f},"
                   f"adelay={ms}|{ms}[e{j}]")
        ef.append(f"[e{j}]")
    fil.append("".join(ef) + f"amix=inputs={len(ef)}:normalize=0:duration=longest,lowpass=f=6500,"
               "aecho=0.8:0.6:35|70:0.18|0.1,apad,atrim=0:" + f"{total:.3f}[sfx]")
    # batería: entra con todo, se agacha bajo la voz, corta al final con fade
    m = b + len(finos)
    ins += ["-i", str(musica)]
    fil.append(f"[{m}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{total:.3f},volume={k_mus},"
               f"afade=t=out:st={total - 1.2:.3f}:d=1.2,apad,atrim=0:{total:.3f}[mus0]")
    fil.append("[mus0][voz_sc]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=350[mus]")
    salida = G / (a[a.index("--salida") + 1] if "--salida" in a else "intro_1986_mezcla.mp4")
    # manifiesto para el Vibe Editor (herramientas/sala.py); --manifiesto = solo eso, sin re-mezclar
    sys.path.insert(0, str(RAIZ / "herramientas"))
    import sala
    t0, piezas = 0.0, []
    for nombre, _ in PIEZAS:
        piezas.append((nombre, G / f"{nombre}.mp4", t0))
        t0 += dur(G / f"{nombre}.mp4")
    pz_voces, k = [], 0
    for (nombre, vs), (_, _, ini) in zip(PIEZAS, piezas):
        for _ in vs:
            pz_voces.append((nombre, voces[k][0], voces[k][1]))
            k += 1
    sala.escribir("argentina-1986", "intro", "Intro · Argentina 86", salida, piezas, pz_voces,
                  [dict(c, vol=c["vol"] * k_sfx) for c in finos], (musica, k_mus), {},
                  {st: salida.with_name(f"{salida.stem}_{st}.wav") for st in ("voz", "mus", "sfx")})
    if "--manifiesto" in a:
        print(salida.with_suffix(".sala.json"))
        return
    extra = []
    if "--stems" in a:                        # además deja voz / batería / efectos sueltos (para medirlos)
        fil.append("[voz]asplit=2[voz][voz_st];[mus]asplit=2[mus][mus_st];[sfx]asplit=2[sfx][sfx_st]")
        for st in ("voz", "mus", "sfx"):
            extra += ["-map", f"[{st}_st]", "-t", f"{total:.3f}", str(salida.with_name(f"{salida.stem}_{st}.wav"))]
    fil.append("[voz][mus][sfx]amix=inputs=3:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[mix]")
    mezcla = salida.with_name(f".{salida.stem}_mezcla.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fil), "-map", "[mix]",
                    "-ar", "48000", "-t", f"{total:.3f}", str(mezcla), *extra], check=True, timeout=600)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista), "-i", str(mezcla),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.3f}",
                    str(salida)], check=True, timeout=600)
    mezcla.unlink()
    print(f"{salida.name}: {total:.1f} s, {len(voces)} frases, {len(finos)} efectos (de {sum(1 for _ in cues)} posibles)")


if __name__ == "__main__":
    main()
