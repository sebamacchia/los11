"""Mezcla de la segunda parte de Argentina 86 en estilo carpeta tranquilo (17/11, herramientas/carpeta_doc.py):
placa del capítulo 1 + escenas p2_1..p2_7, la voz de cada escena (la misma de guion_parte2), la música ochentosa calma
(musica/m86_parte2_80s.mp3) agachada bajo la voz, los efectos de cada pieza bajos y atrás, y la tribuna en los goles
de Pasculli y Gareca.

  herramientas/.venv/bin/python proyectos/argentina-1986/mezcla_parte2.py [--parte 2|3|4] [--vol-musica 0.4] [--stems] [--manifiesto]
  -> salida/graficos/parte2_carpeta.mp4 (capítulo 1) | parte3_carpeta.mp4 (capítulo 2, "El grupo") | parte4_carpeta.mp4 (capítulo 3, "Las camisetas")
"""
import json
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "herramientas"))
import elevenlabs  # noqa: E402
import carpeta_doc as D  # noqa: E402
import sala  # noqa: E402

G = AQUI / "salida" / "graficos"
EL = RAIZ / ".cache" / "elevenlabs"
GOL = "stadium crowd cheering a goal"
PARTES = {  # piezas, voces (una por pieza p*_N, en orden), tribuna/silbato: (pieza, segundo en la voz, prompt, dur, vol)
    "2": (["capitulo1_1986"] + [f"p2_{n}" for n in range(1, 8)], D.VOCES,
          [("p2_2", 4.54, GOL, 2.5, 0.35),
           ("p2_3", 5.88, "stadium crowd erupting in a goal celebration roar", 4, 0.45)]),
    "3": (["capitulo2_1986"] + [f"p3_{n}" for n in range(1, 5)], D.VOCES_C2,
          [("p3_1", 8.1, "referee whistle blow, football match", 1.0, 0.35),
           ("p3_2", 2.3, GOL, 2.5, 0.3),
           ("p3_3", 9.5, GOL, 3, 0.4),
           ("p3_4", 3.4, GOL, 2.5, 0.3)]),
    "4": (["capitulo3_1986"] + [f"p4_{n}" for n in range(1, 5)], D.VOCES_C3,
          [("p4_1", 11.4, GOL, 3, 0.4)]),
    "5": (["capitulo4_1986"] + [f"p5_{n}" for n in range(1, 6)], D.VOCES_C4,
          [("p5_4", 4.4, "huge packed football stadium crowd ambience, 1980s, distant chanting and drums", 3.5, 0.3),
           ("p5_5", 0.0, "football stadium crowd murmur during a tense match, whistles in the distance", 3.0, 0.25)]),
    # p6_3 ("visto desde arriba") sacado el 18/11 por nota del Vibe Editor
    "6": (["capitulo5_1986", "p6_1", "p6_2", "p6_4", "p6_5"], [v for k, v in enumerate(D.VOCES_C5) if k != 2],
          [("p6_1", 17.0, GOL, 3, 0.35), ("p6_4", 3.6, GOL, 3, 0.35)]),
    # p7_3 ("visto desde arriba") sacado el 18/11 por nota del Vibe Editor
    "7": (["capitulo6_1986"] + [f"p7_{n}" for n in (1, 2, 4, 5, 6, 7, 8, 9)],
          [v for k, v in enumerate(D.VOCES_C6) if k != 2],
          [("p7_2", 21.6, "football stadium crowd roaring in celebration of a goal, 1980s", 4, 0.4), ("p7_8", 3.3, "referee final whistle, football", 1.5, 0.3)]),
    "8": (["capitulo7_1986"] + [f"p8_{n}" for n in range(1, 4)], D.VOCES_C7,
          [("p8_1", 12.4, GOL, 3, 0.4), ("p8_2", 10.0, GOL, 3, 0.4)]),
    "9": (["capitulo8_1986"] + [f"p9_{n}" for n in range(1, 11)], D.VOCES_C8,
          [("p9_1", 0.0, "huge packed football stadium crowd ambience, 1980s, chanting and drums", 4, 0.3),
           ("p9_3", 14.4, GOL, 3, 0.4), ("p9_5", 5.1, GOL, 3, 0.4), ("p9_6", 5.8, GOL, 2.5, 0.25),
           ("p9_6", 9.6, GOL, 2.5, 0.25), ("p9_7", 12.2, "football stadium crowd roaring in celebration of a goal, 1980s", 4, 0.45),
           ("p9_9", 2.4, "referee long final whistle, three blows, football", 2.5, 0.4),
           ("p9_10", -0.4, "massive stadium crowd celebrating a world cup title, euphoric singing and screaming", 18, 0.55)]),
    "10": (["capitulo9_1986"] + [f"p10_{n}" for n in range(1, 10)], D.VOCES_C9,
           [("p10_4", 5.0, "huge crowd celebrating in a city square, cheering and singing, distant", 6, 0.25)]),
}
TITULOS = {"2": "Capítulo 1 · Nadie creía", "3": "Capítulo 2 · El grupo", "4": "Capítulo 3 · Las camisetas",
           "5": "Capítulo 4 · La guerra", "6": "Capítulo 5 · La mano de Dios", "7": "Capítulo 6 · El gol del siglo",
           "8": "Capítulo 7 · Bélgica", "9": "Capítulo 8 · La final", "10": "Capítulo 9 · El Mundial de Diego"}
MUSICA = {"2": "m86_parte2_80s.mp3", "3": "m86_cap2_80s.mp3", "4": "m86_cap3_80s.mp3", "5": "m86_cap4_80s.mp3", "6": "m86_inglaterra.mp3",
         "7": "m86_cap6_mix_b.mp3", "8": "m86_relato.mp3", "9": "m86_final.mp3", "10": "m86_cap9_mix.mp3"}


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True).stdout)


def main():
    a = sys.argv
    k_mus = float(a[a.index("--vol-musica") + 1]) if "--vol-musica" in a else 0.4
    parte = a[a.index("--parte") + 1] if "--parte" in a else "2"
    PIEZAS, VOCES, HINCHADA = PARTES[parte]
    t0, inicio = 0.0, {}
    for p in PIEZAS:
        inicio[p] = t0
        t0 += dur(G / f"{p}.mp4")
    total = t0
    # una voz por pieza: hash de ElevenLabs, ruta a un relato real (Víctor Hugo, doña Tota) o None (pieza muda)
    voces = [(v if isinstance(v, Path) else EL / f"voz_{v}.mp3", inicio[p] + D.V)
             for p, v in zip(PIEZAS[1:], VOCES) if v is not None]
    vpiezas = [p for p, v in zip(PIEZAS[1:], VOCES) if v is not None]
    cues = []
    for p in PIEZAS:
        for c in json.load(open(G / f"{p}.sonidos.json")):
            cues.append(dict(c, en=round(inicio[p] + c["en"], 3)))
    for p, wt, prompt, d, vol in HINCHADA:
        try:
            arch = elevenlabs.efecto(prompt, d)
        except (Exception, SystemExit) as e:          # ElevenLabs caído/lento: tribuna libre local (silbatos, nada)
            if "whistle" in prompt:
                print(f"  (sin efecto «{prompt}»: {e})")
                continue
            arch = AQUI / "material/sonidos/hinchada_gol.mp3"
            print(f"  (tribuna local en vez de «{prompt}»: {e})")
        cues.append({"archivo": str(arch), "en": round(inicio[p] + D.V + wt, 3), "desde": 0,
                     "dur": d, "vol": vol / 0.5, "nombre": prompt, "pieza": p})
    salida = G / f"parte{parte}_carpeta.mp4"
    # manifiesto para la SALA (herramientas/sala.py): piezas, capas, palabras, música y cada efecto con su nombre
    nombres = {str(v["archivo"]): k.lower() for k, v in vars(D).items() if isinstance(v, dict) and "archivo" in v
               and str(v["archivo"]).startswith("/")}
    sala.escribir("argentina-1986", f"parte{parte}", TITULOS[parte], salida,
                  [(p, G / f"{p}.mp4", inicio[p]) for p in PIEZAS],
                  [(p, r, en) for p, (r, en) in zip(vpiezas, voces)], cues,
                  (RAIZ / "musica" / MUSICA[parte], k_mus), nombres,
                  {st: salida.with_name(f"{salida.stem}_{st}.wav") for st in ("voz", "mus", "sfx")})
    if "--manifiesto" in a:
        print(salida.with_suffix(".sala.json"))
        return
    # el video se pega SIN re-codificar (todas las piezas salen iguales de carpeta.py: h264 1080p30): la mezcla
    # tarda lo que tarda el audio, así rehacer una sola pieza (rehacer.py) es rápido
    lista = G / f".concat_parte{parte}.txt"
    lista.write_text("".join(f"file '{G / (p + '.mp4')}'\n" for p in PIEZAS))
    ins = []                                   # 1ª pasada: solo audio (mezcla + stems); 2ª: se pega el video
    n = 0
    fil = []
    vz = []
    for j, (r, en) in enumerate(voces):
        ins += ["-i", str(r)]
        ms = int(en * 1000)
        fil.append(f"[{n + j}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[vz{j}]")
        vz.append(f"[vz{j}]")
    fil.append("".join(vz) + f"amix=inputs={len(vz)}:normalize=0:duration=longest,apad,atrim=0:{total:.3f},"
               "asplit=2[voz][voz_sc]")
    b = n + len(voces)
    ef = []
    for j, c in enumerate(cues):
        ins += ["-i", c["archivo"]]
        ms = int(c["en"] * 1000)
        fil.append(f"[{b + j}:a]aresample=48000,aformat=channel_layouts=stereo,atrim={c['desde']}:{c['desde'] + c['dur']},"
                   f"asetpts=PTS-STARTPTS,afade=t=out:st={max(0, c['dur'] - 0.4)}:d=0.4,volume={c['vol'] * 0.5:.3f},"
                   f"adelay={ms}|{ms}[e{j}]")
        ef.append(f"[e{j}]")
    fil.append("".join(ef) + f"amix=inputs={len(ef)}:normalize=0:duration=longest,lowpass=f=7000,"
               "aecho=0.8:0.6:35|70:0.18|0.1,apad,atrim=0:" + f"{total:.3f}[sfx]")
    m = b + len(cues)
    ins += ["-stream_loop", "-1", "-i", str(RAIZ / "musica" / MUSICA[parte])]   # si el capítulo es más largo, vuelve a empezar
    fil.append(f"[{m}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{total:.3f},volume={k_mus},"
               f"afade=t=in:d=1.0,afade=t=out:st={total - 2.0:.3f}:d=2.0,apad,atrim=0:{total:.3f}[mus0]")
    fil.append("[mus0][voz_sc]sidechaincompress=threshold=0.03:ratio=4:attack=30:release=500[mus]")
    extra = []
    if "--stems" in a:
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
    print(f"{salida.name}: {total:.1f} s, {len(voces)} frases, {len(cues)} efectos")


if __name__ == "__main__":
    main()
