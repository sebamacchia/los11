"""MESA DE GUION — la conversación humano ↔ Claude sobre un guion, escena por escena (la sirve estudio.py en /mesa).

Por escena se ve: lo que dice el narrador · qué pasa en imagen · música y efectos · el hilo de mensajes.
Los mensajes del humano quedan en proyectos/<p>/mesa/<guion>.json y además en la bandeja .cache/mesa_bandeja.jsonl,
que Claude escucha (Monitor) para responder. Claude contesta con:
  /usr/bin/python3 herramientas/estudio.py responder <proyecto> <guion> <escena|general> "texto"   (escena = número 1..N)
  /usr/bin/python3 herramientas/estudio.py pendientes [<proyecto>]                                  (lo que falta contestar)
Los cambios de narración que escribe el humano son PROPUESTAS (tipo "cambio"): Claude los aplica en la fuente
(guion o construir_*.py), regenera y responde.
"""
import json
import re
import subprocess
import time
import unicodedata
import uuid
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PROY = RAIZ / "proyectos"
BANDEJA = RAIZ / ".cache" / "mesa_bandeja.jsonl"
ESCUCHA = RAIZ / ".cache" / "mesa_escucha"       # Claude lo toca mientras escucha
CUADROS = RAIZ / ".cache" / "mesa_cuadros"


def _norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9ñ ]+", "", "".join(ch for ch in s if unicodedata.category(ch) != "Mn")).split()


def _srt(path):
    if not path.exists():
        return []
    out = []
    for bloque in path.read_text().strip().split("\n\n"):
        ls = bloque.splitlines()
        if len(ls) < 3:
            continue
        a, b = ls[1].split(" --> ")
        seg = lambda x: (lambda h, m, s: int(h) * 3600 + int(m) * 60 + float(s.replace(",", ".")))(*x.split(":"))
        out.append((seg(a), seg(b), " ".join(ls[2:])))
    return out


def tiempos_escenas(guion, srt):
    """Inicio/fin de cada escena en el video renderizado, emparejando las frases del .srt con el texto."""
    res, j = [], 0
    for e in guion["escenas"]:
        palabras = _norm(e.get("texto", ""))
        if not palabras or j >= len(srt):
            res.append(None)
            continue
        ini, k, usadas = srt[j][0], j, 0
        while k < len(srt):
            p = _norm(srt[k][2])
            if p and palabras[usadas:usadas + len(p)] == p:
                usadas += len(p)
                k += 1
            else:
                break
        if k == j:  # no calzó: buscar la primera frase más adelante
            res.append(None)
            continue
        res.append([round(ini, 2), round(srt[k - 1][1], 2)])
        j = k
    return res


def archivo_conv(p, g):
    return PROY / p / "mesa" / f"{g}.json"


def leer_conv(p, g):
    f = archivo_conv(p, g)
    return json.loads(f.read_text()) if f.exists() else {"hilos": {}}


def guardar_conv(p, g, conv):
    f = archivo_conv(p, g)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(conv, ensure_ascii=False, indent=2) + "\n")


def guiones(p):
    return sorted(f.stem for f in (PROY / p).glob("guion*.json") if not f.stem.endswith("_en"))


def estado(p, g):
    gpath = PROY / p / f"{g}.json"
    guion = json.loads(gpath.read_text())
    sufijo = "" if g == "guion" else "_" + g
    srt = _srt(PROY / p / "salida" / f"subtitulos{sufijo}.srt")
    video = None
    for nombre in (f"{guion.get('archivo', p)}.mp4", f"{guion.get('archivo', p)}.borrador.mp4"):
        if (PROY / p / "salida" / nombre).exists():
            video = f"salida/{nombre}?v={int((PROY / p / 'salida' / nombre).stat().st_mtime)}"
            break
    conv = leer_conv(p, g)
    escucha = ESCUCHA.exists() and time.time() - ESCUCHA.stat().st_mtime < 20
    return {"guion": guion, "tiempos": tiempos_escenas(guion, srt), "video": video, "conv": conv,
            "mtime_guion": gpath.stat().st_mtime, "mtime_conv": archivo_conv(p, g).stat().st_mtime if archivo_conv(p, g).exists() else 0,
            "escucha": escucha}


def mensaje(p, g, escena, de, texto, columna="general", tipo="nota", extra=None, borrador=False):
    """borrador=True: la nota queda guardada en la conversación pero NO va a la bandeja (Claude no la ve) hasta que el
    humano aprieta "Mandar todo" (ver enviar_borradores)."""
    conv = leer_conv(p, g)
    m = {"id": uuid.uuid4().hex[:10], "de": de, "texto": texto, "columna": columna, "tipo": tipo,
         "fecha": time.strftime("%Y-%m-%d %H:%M:%S"), **(extra or {})}
    if borrador:
        m["borrador"] = True
    hilo = conv["hilos"].setdefault(str(escena), [])
    if de == "claude":
        for x in hilo:
            if x["de"] == "humano" and not x.get("borrador"):
                x["respondido"] = True
    hilo.append(m)
    guardar_conv(p, g, conv)
    if de == "humano" and not borrador:
        BANDEJA.parent.mkdir(exist_ok=True)
        with open(BANDEJA, "a") as f:
            f.write(json.dumps({"proyecto": p, "guion": g, "escena": escena, **m}, ensure_ascii=False) + "\n")
    return m


def borradores(p):
    """Notas guardadas sin mandar, de todos los cortes del proyecto: [{guion, escena, id, texto, t...}]."""
    out = []
    for f in sorted((PROY / p / "mesa").glob("*.json")) if (PROY / p / "mesa").is_dir() else []:
        for esc, hilo in json.loads(f.read_text())["hilos"].items():
            out += [{"guion": f.stem, "escena": esc, **m} for m in hilo if m.get("borrador")]
    return out


def enviar_borradores(p):
    """"Mandar todo": cada borrador pasa a nota normal y entra a la bandeja (con su corte, pieza y segundo)."""
    n = 0
    BANDEJA.parent.mkdir(exist_ok=True)
    for f in sorted((PROY / p / "mesa").glob("*.json")) if (PROY / p / "mesa").is_dir() else []:
        conv = json.loads(f.read_text())
        cambio = False
        for esc, hilo in conv["hilos"].items():
            for m in hilo:
                if m.pop("borrador", False):
                    m["enviada"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    with open(BANDEJA, "a") as b:
                        b.write(json.dumps({"proyecto": p, "guion": f.stem, "escena": esc, **m}, ensure_ascii=False) + "\n")
                    n += 1
                    cambio = True
        if cambio:
            guardar_conv(p, f.stem, conv)
    return n


def borrar_borrador(p, g, id_):
    conv = leer_conv(p, g)
    for hilo in conv["hilos"].values():
        hilo[:] = [m for m in hilo if not (m.get("borrador") and m["id"] == id_)]
    conv["hilos"] = {k: v for k, v in conv["hilos"].items() if v}
    guardar_conv(p, g, conv)
    return {"ok": True}


def pendientes(p=None):
    out = []
    for d in ([PROY / p] if p else sorted(PROY.iterdir())):
        for f in sorted((d / "mesa").glob("*.json")) if (d / "mesa").is_dir() else []:
            conv = json.loads(f.read_text())
            for esc, hilo in conv["hilos"].items():
                for m in hilo:
                    if m["de"] == "humano" and not m.get("respondido") and not m.get("borrador"):
                        out.append({"proyecto": d.name, "guion": f.stem, "escena": esc, **m})
    return out


def cuadro(p, ruta, t):
    """Miniatura jpg de una foto o de un cuadro de video (cacheada)."""
    src = (PROY / p / ruta).resolve()
    if PROY.resolve() not in src.parents and RAIZ.resolve() not in src.parents:
        raise PermissionError(ruta)
    CUADROS.mkdir(parents=True, exist_ok=True)
    out = CUADROS / (re.sub(r"[^\w]+", "_", f"{p}_{ruta}_{float(t):.1f}") + ".jpg")
    if not out.exists():
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{float(t):.2f}", "-i", str(src), "-frames:v", "1",
                        "-vf", "scale=320:-2", "-q:v", "4", str(out)], check=True, timeout=60)
    return out
