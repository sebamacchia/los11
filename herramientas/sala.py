"""VIBE EDITOR (antes "SALA") — sala de edición del director para los capítulos en carpeta (17/11, pedido del usuario: "una interfaz donde
podamos ver todo y hacer comentarios y mandártelos: del script, de la forma que lo dice, de la animación, de la música,
de los sfx... más fácil que FilmCraft").

La sirve estudio.py en http://localhost:8770/vibe (también /sala). Cada "corte" (un capítulo mezclado) tiene un manifiesto
salida/graficos/<corte>.sala.json que escribe la mezcla (mezcla_parte2.py, también con --manifiesto sin re-mezclar):
video, stems, piezas con sus capas (cada animación con nombre e intervalo), voces con palabras (whisper), música y
cada efecto (nombre, a qué elemento pertenece).

Las notas del humano se guardan con mesa.mensaje en proyectos/<p>/mesa/sala_<corte>.json (+ bandeja
.cache/mesa_bandeja.jsonl, la misma que escucha Claude). Claude contesta:
  /usr/bin/python3 herramientas/estudio.py responder <proyecto> sala_<corte> <pieza|general> "texto"
"""
import json
import re
import subprocess
import time
from pathlib import Path

import mesa

RAIZ = Path(__file__).resolve().parent.parent
PROY = RAIZ / "proyectos"
WHISPER = RAIZ / ".cache" / "whisper" / "ggml-large-v3-turbo-q5_0.bin"
PALABRAS = RAIZ / ".cache" / "whisper_palabras"


def _dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout)
    except ValueError:
        return 0.0


def palabras(mp3):
    """Palabras con tiempos (whisper local, cacheado por archivo): [{"w", "t0", "t1"}]."""
    mp3 = Path(mp3)
    PALABRAS.mkdir(parents=True, exist_ok=True)
    cache = PALABRAS / f"{mp3.stem}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    wav = PALABRAS / f"_{mp3.stem}.wav"          # la salida cruda de whisper (_x.json) no pisa la caché (x.json)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp3), "-ar", "16000", "-ac", "1", str(wav)], check=True)
    subprocess.run(["whisper-cli", "-m", str(WHISPER), "-l", "es", "-ml", "1", "-oj", "-of", str(wav.with_suffix("")),
                    "-f", str(wav)], check=True, capture_output=True)
    # whisper a veces corta una letra con tilde entre dos tokens: se leen los bytes tal cual y se arma al final
    d = json.loads(wav.with_suffix(".json").read_bytes().decode("utf-8", "surrogateescape"))
    out = []
    for s in d["transcription"]:
        tx, a, b = s["text"], s["offsets"]["from"] / 1000, s["offsets"]["to"] / 1000
        if not tx.strip():
            continue
        if tx.startswith(" ") or not out or not tx.strip()[0].isalnum():
            if out and not tx.startswith(" "):          # puntuación pegada a la palabra anterior
                out[-1]["w"] += tx.strip()
                out[-1]["t1"] = round(b, 2)
                continue
            out.append({"w": tx.strip(), "t0": round(a, 2), "t1": round(b, 2)})
        else:
            out[-1]["w"] += tx
            out[-1]["t1"] = round(b, 2)
    for x in out:
        x["w"] = x["w"].encode("utf-8", "surrogateescape").decode("utf-8", "replace")
    wav.unlink(missing_ok=True)
    wav.with_suffix(".json").unlink(missing_ok=True)
    cache.write_text(json.dumps(out, ensure_ascii=False))
    return out


def _capas(mp4):
    """Elementos de una pieza: <pieza>.elementos.json (lo escribe carpeta_doc al renderizar) o, si no hay o es más
    viejo que el video, las capas ProRes (<pieza>_capas/capas.json)."""
    mp4 = Path(mp4)
    el = mp4.with_suffix(".elementos.json")
    if el.exists() and el.stat().st_mtime >= mp4.stat().st_mtime - 5:
        return [{"nombre": e["nombre"], "inicio": round(e["inicio"], 2), "fin": round(e["fin"], 2)}
                for e in json.loads(el.read_text())]
    dir_capas = mp4.with_name(f"{mp4.stem}_capas")
    f = Path(dir_capas) / "capas.json"
    if not f.exists():
        return []
    out = []
    for c in json.loads(f.read_text())["capas"]:
        d = _dur(Path(dir_capas) / c["archivo"])
        out.append({"nombre": c["nombre"], "inicio": round(c["inicio"], 2), "fin": round(c["inicio"] + d, 2)})
    return out


def _nombre_sfx(archivo, nombres):
    if archivo in nombres:
        return nombres[archivo]
    return Path(archivo).stem.replace("_", " ")


def escribir(proyecto, corte, titulo, video, piezas, voces, cues, musica, nombres_sfx=None, stems=None):
    """piezas: [(nombre, mp4, inicio)]; voces: [(pieza, mp3, inicio_global)]; cues: dicts con archivo/en/dur/vol
    (en global) y opcional "pieza"; musica: (archivo, vol). Escribe <video sin .mp4>.sala.json."""
    base = PROY / proyecto
    rel = lambda p: str(Path(p).resolve().relative_to(base.resolve())) if base.resolve() in Path(p).resolve().parents \
        else str(Path(p).resolve().relative_to(RAIZ.resolve()))
    ps = []
    for nombre, mp4, ini in piezas:
        mp4 = Path(mp4)
        ps.append({"nombre": nombre, "inicio": round(ini, 3), "dur": round(_dur(mp4), 3),
                   "capas": _capas(mp4)})
    vs = [{"pieza": pz, "archivo": rel(mp3), "inicio": round(ini, 3), "palabras": palabras(mp3)} for pz, mp3, ini in voces]
    sf = []
    for c in cues:
        pz = c.get("pieza") or next((p["nombre"] for p in reversed(ps) if p["inicio"] <= c["en"] + 1e-3), None)
        elemento = None
        p = next((x for x in ps if x["nombre"] == pz), None)
        if p:
            loc = c["en"] - p["inicio"]
            cand = [k for k in p["capas"] if k["inicio"] <= loc + 0.05 and loc - k["inicio"] < 0.7]
            if cand:
                elemento = max(cand, key=lambda k: k["inicio"])["nombre"]
        sf.append({"nombre": c.get("nombre") or _nombre_sfx(c["archivo"], nombres_sfx or {}), "archivo": rel(c["archivo"]),
                   "en": round(c["en"], 3), "dur": round(c["dur"], 2), "vol": round(c.get("vol", 1), 2),
                   "pieza": pz, "elemento": elemento})
    m = {"proyecto": proyecto, "corte": corte, "titulo": titulo, "video": rel(video), "dur": round(_dur(video), 3),
         "stems": {k: rel(v) for k, v in (stems or {}).items() if Path(v).exists()},
         "piezas": ps, "voces": vs, "sfx": sf,
         "musica": {"archivo": rel(musica[0]), "nombre": Path(musica[0]).stem, "vol": musica[1]},
         "generado": time.strftime("%Y-%m-%d %H:%M:%S")}
    out = Path(video).with_suffix(".sala.json")
    out.write_text(json.dumps(m, ensure_ascii=False, indent=1))
    return out


def cortes(proyecto):
    out = []
    def orden(f):                                   # intro primero, después parte2, parte3... parte10
        n = re.findall(r"\d+", f.stem)
        return (0 if "intro" in f.stem else 1, int(n[0]) if n else 0, f.stem)
    for f in sorted((PROY / proyecto / "salida").rglob("*.sala.json"), key=orden):
        m = json.loads(f.read_text())
        out.append({"corte": m["corte"], "titulo": m["titulo"]})
    return out


def _manifiesto(proyecto, corte):
    for f in (PROY / proyecto / "salida").rglob("*.sala.json"):
        m = json.loads(f.read_text())
        if m["corte"] == corte:
            return f, m
    raise KeyError(corte)


def estado(proyecto, corte):
    f, m = _manifiesto(proyecto, corte)
    g = f"sala_{corte}"
    conv = mesa.leer_conv(proyecto, g)
    vid = PROY / proyecto / m["video"]
    m["video_v"] = int(vid.stat().st_mtime) if vid.exists() else 0
    escucha = mesa.ESCUCHA.exists() and time.time() - mesa.ESCUCHA.stat().st_mtime < 20
    fc = mesa.archivo_conv(proyecto, g)
    return {"m": m, "conv": conv, "mtime_conv": fc.stat().st_mtime if fc.exists() else 0,
            "mtime_m": f.stat().st_mtime, "escucha": escucha}


def nota(proyecto, corte, d):
    """Nota del humano: d = {texto, tipo (guion|voz|animacion|musica|sfx|general), pieza, t, pista, elemento, x, y,
    palabras, decir}."""
    tipo = d.get("tipo", "general")
    extra = {k: d[k] for k in ("t", "pista", "elemento", "x", "y", "palabras", "decir", "t1") if d.get(k) not in (None, "")}
    return mesa.mensaje(proyecto, f"sala_{corte}", d.get("pieza") or "general", "humano", d["texto"], tipo, "nota", extra,
                        borrador=bool(d.get("borrador")))
