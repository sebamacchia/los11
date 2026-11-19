"""Sampler casero: corta golpes sueltos de un archivo (varios hits con silencio entre medio) y arma piezas musicales
"tipo MIDI" con esos sonidos reales (17/11, intro de Argentina 86: batería de jazz + contrabajo de ElevenLabs SFX).

  herramientas/.venv/bin/python herramientas/sampler.py cortar <crudos/> <salida/>   -> <inst>_<n>.wav + muestras.json

Cada muestra: arranca 4 ms antes del ataque, termina cuando cae 50 dB bajo el pico (o al tope del instrumento), con
fundido de 15 ms. En los instrumentos con nota (bass) mide la frecuencia fundamental por autocorrelación.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

SR = 48000
TOPE = {"kick": 0.9, "snare": 0.7, "ghost": 0.4, "ride": 3.0, "hihat": 0.35, "crash": 3.5, "tomhi": 1.0, "tomlo": 1.2,
        "bass": 1.8}


def leer(ruta):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ruta), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="float32").copy()


def escribir(ruta, x):
    x = np.clip(x, -1, 1).astype("float32")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", str(ruta)],
                   input=x.tobytes(), check=True)


def envolvente(x, ms=5):
    n = max(1, int(SR * ms / 1000))
    return np.sqrt(np.convolve(x * x, np.ones(n) / n, mode="same"))


def golpes(x, tope):
    """Ataques: la envolvente sube por encima del 12 % del pico después de haber estado abajo del 3 %."""
    x = x / max(1e-6, np.abs(x).max())           # ElevenLabs a veces entrega golpes muy bajos (pico 0.005)
    e = envolvente(x)
    pico = e.max()
    hits, armado, i = [], True, 0
    while i < len(x):
        if armado and e[i] > 0.12 * pico:
            a = i
            while a > 0 and e[a] > 0.03 * pico:      # retrocede al pie del ataque
                a -= 1
            hits.append(a)
            armado = False
            i += int(0.08 * SR)
            continue
        if not armado and e[i] < 0.03 * pico:
            armado = True
        i += 1
    out = []
    for k, a in enumerate(hits):
        fin_max = min(len(x), a + int(tope * SR), hits[k + 1] - int(0.005 * SR) if k + 1 < len(hits) else len(x))
        seg = x[max(0, a - int(0.004 * SR)):fin_max].copy()
        es = envolvente(seg, 10)
        p = es.max()
        bajo = np.where(es[np.argmax(es):] < p * 10 ** (-50 / 20))[0]
        if len(bajo):
            seg = seg[:np.argmax(es) + bajo[0]]
        f = min(len(seg), int(0.015 * SR))
        seg[-f:] *= np.linspace(1, 0, f)
        if len(seg) > int(0.03 * SR) and np.abs(seg).max() > 0.02:
            out.append(seg / np.abs(seg).max() * 0.9)
    return out


def f0(seg):
    """Fundamental (Hz) por producto armónico del espectro (30-300 Hz), en la parte estable después del ataque."""
    s = seg[int(0.05 * SR):int(0.8 * SR)]
    s = (s - s.mean()) * np.hanning(len(s))
    n = 1 << 18
    X = np.abs(np.fft.rfft(s, n))
    hps = X.copy()
    for h in (2, 3, 4):
        d = X[::h]
        hps[:len(d)] *= d
    fr = np.fft.rfftfreq(n, 1 / SR)
    m = (fr > 30) & (fr < 300)
    return float(fr[m][np.argmax(hps[m])])


def cortar(crudos, salida):
    """Un golpe por archivo (el primero): <inst><toma>.mp3 -> <inst>_<toma>.wav."""
    crudos, salida = Path(crudos), Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    info = {}
    for f in sorted(crudos.glob("*.mp3")):
        inst = f.stem.rstrip("0123456789")
        segs = golpes(leer(f), TOPE.get(inst, 1.5))
        if not segs:
            print("sin golpe:", f.name)
            continue
        s = segs[0]
        n = len(info.setdefault(inst, [])) + 1
        r = salida / f"{inst}_{n}.wav"
        escribir(r, s)
        d = {"archivo": r.name, "dur": round(len(s) / SR, 3), "crudo": f.name}
        if inst == "bass":
            d["hz"] = round(f0(s), 2)
        info[inst].append(d)
    for inst, l in info.items():
        print(inst, [d.get("hz", d["dur"]) for d in l])
    json.dump(info, open(salida / "muestras.json", "w"), indent=1)


if __name__ == "__main__":
    if sys.argv[1] == "cortar":
        cortar(sys.argv[2], sys.argv[3])
