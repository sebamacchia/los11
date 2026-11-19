"""Música de la intro de Argentina 86 hecha "tipo MIDI" con sonidos sueltos reales (17/11, pedido del usuario):
golpes de batería de jazz y notas de contrabajo generados con ElevenLabs SFX, cortados con herramientas/sampler.py
(musica/samples/jazz86/, verificados con earshot) y secuenciados acá: swing con ride, hi-hat en 2 y 4, ghost notes,
walking bass sobre un blues en Fa, y los golpes atados a la intro:
  2.45 s sello 1986 (entra la banda) · cambios de pieza con platillo · 47.79 peluca (corte) · stop-time en
  "subite / sentate / callate / agarrate" · redoble en el despegue del DeLorean · 55.25 "LOS ONCE" (vuelve el swing)
  · 68.25 "blanco" (golpe final).

  herramientas/.venv/bin/python proyectos/argentina-1986/jazz_intro.py [--semilla 3] [--libre]
  -> musica/intro86_jazz_samples.wav (o intro86_jazz_libre.wav) + .mid (para abrirlo en cualquier DAW) + .json

--libre (17/11, "que suene orgánico, no tan steady, golpes sueltos, más experimental"): sin grilla fija. El tempo
respira (paseo al azar), la batería toca por gestos (frases de ride que se cortan, golpes sueltos, ráfagas de toms,
nubes de ghosts, silencios), acentos en los momentos de la imagen (intro_1986_mezcla_cues.json) con platillo al revés
que crece antes de algunos, y el contrabajo toca notas sueltas largas, a veces con glissando.
"""
import json
import random
import struct
import subprocess
import sys
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "herramientas"))
import sampler  # noqa: E402

SR = sampler.SR
MU = RAIZ / "musica" / "samples" / "jazz86"
TOTAL = 70.167
T0, PELUCA = 2.45, 47.793                 # entra la banda (sello 1986) / vuela la peluca
CIERRE = 49.267                           # arranca la pieza del cierre
ORDENES = [CIERRE + t for t in (0.76, 1.69, 2.71, 3.47)]    # subite, sentate, callate, agarrate
LOS11, BLANCO = CIERRE + 5.98, CIERRE + 18.98
CAMBIOS = [19.133, 32.033]                # cambios de pieza: platillo en el tiempo más cercano
COMPASES_A = 30
BAR = (PELUCA - T0) / COMPASES_A          # 1.511 s -> ~159 bpm
BEAT = BAR / 4
SWING = 2 / 3                             # corchea swingueada (tresillo)

# muestras a usar (las que earshot reconoció bien; ghost = redoblante suave y opaco)
USAR = {"kick": ["kick_2", "kick_3"], "snare": ["snare_2", "snare_3", "snare_1"], "ride": ["ride_2", "ride_3", "ride_1"],
        "hihat": ["hihat_1", "hihat_3", "hihat_2"], "crash": ["crash_1"], "tomhi": ["tomhi_1"], "tomlo": ["tomlo_1"]}
PAN = {"kick": 0.0, "snare": 0.05, "ghost": 0.05, "ride": 0.35, "hihat": -0.3, "crash": 0.25, "tomhi": -0.15,
       "tomlo": 0.2, "bass": 0.0}
GM = {"kick": 36, "snare": 38, "ghost": 38, "ride": 51, "hihat": 44, "crash": 49, "tomhi": 48, "tomlo": 43}


def cargar():
    S = {k: [sampler.leer(MU / f"{n}.wav") for n in v] for k, v in USAR.items()}
    # ghost: el mismo redoblante, opaco (pasabajos de un polo) y más corto
    S["ghost"] = []
    for x in S["snare"]:
        y = np.zeros_like(x)
        a = 0.18
        for i in range(1, len(x)):
            y[i] = y[i - 1] + a * (x[i] - y[i - 1])
        S["ghost"].append(y[:int(0.25 * SR)] / np.abs(y).max())
    info = json.load(open(MU / "muestras.json"))
    S["bass"] = [(sampler.leer(MU / d["archivo"]), d["hz"]) for d in info["bass"]]
    return S


def nota_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def afinar(x, f_src, f_dst):
    r = f_dst / f_src
    idx = np.arange(0, len(x) - 1, r)
    return np.interp(idx, np.arange(len(x)), x).astype("float32")


def glis(x, f_src, f0, f1):
    """Nota que se desliza de f0 a f1 (el contrabajo arrastrando el dedo)."""
    n = len(x)
    r = np.linspace(f0, f1, n) / f_src
    pos = np.cumsum(r)
    pos = pos[pos < n - 1]
    return np.interp(pos, np.arange(n), x).astype("float32")


class Pista:
    def __init__(self):
        self.L = np.zeros(int((TOTAL + 4) * SR), dtype="float32")
        self.R = np.zeros_like(self.L)
        self.notas = []

    def pon(self, x, t, vel, pan, inst, midi=None, dur=None):
        i = int(t * SR)
        if i < 0 or i >= len(self.L):
            return
        x = x[:len(self.L) - i] * vel
        self.L[i:i + len(x)] += x * (1 - pan) * 0.5
        self.R[i:i + len(x)] += x * (1 + pan) * 0.5
        self.notas.append({"t": round(t, 4), "inst": inst, "vel": round(vel, 3), "midi": midi,
                           "dur": round(dur or len(x) / SR, 3)})


def walking(compases, rnd):
    """Walking bass en negras sobre blues en Fa (12 compases). Devuelve notas MIDI por compás."""
    acordes = ["F7", "Bb7", "F7", "F7", "Bb7", "Bb7", "F7", "D7", "Gm7", "C7", "F7", "C7"]
    tonos = {"F7": [29, 33, 36, 39], "Bb7": [34, 38, 41, 44], "D7": [26, 30, 33, 36], "Gm7": [31, 34, 38, 41],
             "C7": [36, 40, 43, 46]}
    out, prev = [], 29
    for c in range(compases):
        ac = acordes[c % 12]
        sig = acordes[(c + 1) % 12]
        raiz = tonos[ac][0]
        while raiz - prev > 6:
            raiz -= 12
        while prev - raiz > 6:
            raiz += 12
        raiz = max(28, min(raiz, 43))
        t3 = raiz + (tonos[ac][1] - tonos[ac][0])
        t5 = raiz + (tonos[ac][2] - tonos[ac][0])
        dest = tonos[sig][0]
        while dest - t5 > 7:
            dest -= 12
        while t5 - dest > 7:
            dest += 12
        aprox = dest + rnd.choice([-1, 1])
        out.append([raiz, rnd.choice([t3, t5]), rnd.choice([t5, raiz + 12 if raiz + 12 <= 45 else t3]), aprox])
        prev = aprox
    return out


def main():
    a = sys.argv
    rnd = random.Random(int(a[a.index("--semilla") + 1]) if "--semilla" in a else 3)
    S = cargar()
    libre = "--libre" in a
    if libre:                                                      # platillos oscuros (pasabajos ~2.5 kHz)
        from scipy.signal import butter, lfilter
        bb, aa = butter(2, 2500 / (SR / 2))
        for k in ("ride", "crash", "hihat"):
            S[k] = [lfilter(bb, aa, x).astype("float32") / max(1e-6, np.abs(lfilter(bb, aa, x)).max()) for x in S[k]]
    P = Pista()

    def hum(ms=6):
        return rnd.uniform(-ms, ms) / 1000

    def d(inst, t, vel):
        if libre and inst in ("crash", "ride", "hihat"):          # 17/11: "demasiados platillos, muy agudo"
            vel *= {"crash": 0.4, "ride": 0.55, "hihat": 0.6}[inst]
        P.pon(rnd.choice(S[inst]), t + hum(), vel * rnd.uniform(0.9, 1.05), PAN[inst], inst, GM[inst])

    def bajo(m, t, vel=0.85, largo=None):
        x, f = min(S["bass"], key=lambda s: abs(12 * np.log2(nota_hz(m) / s[1])))
        y = afinar(x, f, nota_hz(m))
        if largo:
            n = int(largo * SR)
            y = y[:n].copy()
            k = min(len(y), int(0.03 * SR))
            y[-k:] *= np.linspace(1, 0, k)
        P.pon(y, t + hum(4), vel, PAN["bass"], "bass", m, largo)

    def swing(desde, compases, walk, platillos=()):
        for c in range(compases):
            b0 = desde + c * BAR
            for k in range(4):
                t = b0 + k * BEAT
                d("ride", t - 0.004, 0.62 if k in (0, 2) else 0.78)
                if k in (1, 3):
                    d("ride", t + SWING * BEAT - 0.004, 0.5)
                    d("hihat", t, 0.55)
                d("kick", t, 0.13)                                   # feathering
                bajo(walk[c][k], t, 0.8 if k == 0 else 0.7, largo=BEAT * 0.95)
                off = t + SWING * BEAT
                r = rnd.random()
                if r < 0.2:
                    d("ghost", off, rnd.uniform(0.18, 0.3))
                elif r < 0.25:
                    d("snare", off, 0.5)
                    if rnd.random() < 0.5:
                        d("kick", off, 0.45)                         # "bomba"
            if c % 8 == 7 and c != compases - 1:                     # pequeño redoble cada 8 compases
                t = b0 + 3 * BEAT
                for j, inst in enumerate(["snare", "snare", "tomhi"]):
                    d(inst, t + j * BEAT / 3, 0.45 + 0.1 * j)
        for t in platillos:
            d("crash", t, 0.6)
            d("kick", t, 0.5)


    def tramo_libre(desde, hasta, acentos):
        """Batería por gestos, tempo que respira; acentos [(t, tipo)] en los momentos de la imagen."""
        t, b = desde, BEAT
        while t < hasta - 0.3:
            b = min(BEAT * 1.25, max(BEAT * 0.8, b * rnd.uniform(0.93, 1.07)))
            g = rnd.choices(["ride", "silencio", "rafaga", "suelto", "ghosts"], [12, 40, 9, 27, 12])[0]
            if g == "ride":
                for k in range(rnd.randint(2, 4)):
                    tt = t + (k // 2) * b + (k % 2) * SWING * b
                    if tt >= hasta:
                        break
                    d("ride", tt, rnd.uniform(0.35, 0.75))
                    if k % 2 == 1 and rnd.random() < 0.2:
                        d("hihat", tt - SWING * b + b, 0.4)
                    if rnd.random() < 0.15:
                        d("ghost", tt + SWING * b, rnd.uniform(0.15, 0.3))
                t = tt + b * rnd.uniform(0.6, 1.4)
            elif g == "silencio":
                if rnd.random() < 0.5:
                    d("ride", t, rnd.uniform(0.2, 0.4))
                t += rnd.uniform(1.0, 2.6)
            elif g == "rafaga":
                n = rnd.randint(4, 11)
                paso = b / rnd.choice([3, 4, 5])
                sube = rnd.random() < 0.6
                for k in range(n):
                    u = k / max(1, n - 1)
                    inst = rnd.choice(["snare", "tomhi", "tomlo"]) if u > 0.4 else "snare"
                    d(inst, t + k * paso * rnd.uniform(0.85, 1.15), 0.2 + 0.55 * (u if sube else 1 - u))
                t += n * paso + rnd.uniform(0.2, 0.6)
            elif g == "suelto":
                for k in range(rnd.randint(1, 3)):
                    x = rnd.random()
                    if x < 0.35:
                        d("kick", t, rnd.uniform(0.5, 0.85))
                        d("snare", t + 0.004, rnd.uniform(0.4, 0.7))
                    elif x < 0.6:
                        d("tomlo", t, rnd.uniform(0.4, 0.8))
                    elif x < 0.8:                                   # flam
                        d("ghost", t - 0.025, 0.35)
                        d("snare", t, rnd.uniform(0.5, 0.75))
                    else:
                        d("tomhi", t, rnd.uniform(0.4, 0.7))
                    t += rnd.uniform(0.5, 1.4)
            else:
                for k in range(rnd.randint(5, 12)):
                    d("ghost", t, rnd.uniform(0.1, 0.28))
                    t += rnd.uniform(0.05, 0.16)
                t += rnd.uniform(0.2, 0.5)
        for ta, tipo in acentos:
            if not (desde <= ta < hasta):
                continue
            if tipo in ("whoosh_grave", "avion_pasa") and rnd.random() < 0.3:
                rv = rnd.choice(S["ride"])[:int(1.1 * SR)][::-1].copy()
                P.pon(rv * np.linspace(0, 1, len(rv)) ** 1.5, ta - len(rv) / SR, 0.55, 0.3, "ride_rev")
            elif tipo == "libro_cae":
                d("tomlo", ta, 0.85)
                d("kick", ta, 0.8)
            elif tipo == "sello_thump":
                d("kick", ta, 0.75)
                d("snare", ta, 0.7)
                pass
            elif tipo == "auto_pasa":
                for k in range(8):
                    d("tomhi" if k % 2 else "tomlo", ta - 0.5 + k * 0.07, 0.3 + 0.07 * k)

    def bajo_libre(desde, hasta):
        """Notas sueltas largas, a veces con glissando; pocas, con aire entre medio."""
        t = desde + rnd.uniform(0.2, 1.0)
        notas = [29, 31, 32, 34, 36, 39, 41, 24, 27]          # Fa menor con alguna disonancia
        while t < hasta - 0.5:
            m = rnd.choice(notas)
            x, f = min(S["bass"], key=lambda s: abs(12 * np.log2(nota_hz(m) / s[1])))
            if rnd.random() < 0.3:
                m2 = m + rnd.choice([-5, -2, -1, 1, 2, 3, 5])
                y = glis(x, f, nota_hz(m), nota_hz(m2))
                P.pon(y, t, rnd.uniform(0.6, 0.85), 0.0, "bass", m)
            else:
                bajo(m, t, rnd.uniform(0.55, 0.9))
            if rnd.random() < 0.35:                            # segunda nota pegada (frase corta)
                bajo(rnd.choice(notas), t + rnd.uniform(0.25, 0.5), rnd.uniform(0.45, 0.7))
            t += rnd.uniform(1.4, 3.8)

    cues = json.load(open(AQUI / "salida/graficos/intro_1986_mezcla_cues.json"))
    acentos = [(c["en"], Path(c["archivo"]).stem) for c in cues]

    # 0 - 2.45: VHS; el hi-hat marca el tiempo (cuenta) y un redoble chico de entrada
    for k in range(-6, 0):
        d("hihat", T0 + k * BEAT, 0.45 if k % 2 else 0.35)
    for j in range(3):
        d("snare", T0 - BEAT + j * BEAT / 3, 0.35 + 0.15 * j)
    # A: 2.45 - 47.79 (30 compases), platillo al entrar y en los cambios de pieza
    plat = [T0] + [T0 + round((c - T0) / BEAT) * BEAT for c in CAMBIOS]
    if libre:
        for tp in plat:
            d("kick", tp, 0.6)
            d("tomlo", tp, 0.5)
        tramo_libre(T0, PELUCA - BEAT, acentos)
        bajo_libre(T0, PELUCA - BEAT)
    else:
        swing(T0, COMPASES_A, walking(COMPASES_A, rnd), plat)
    # el último compás de A termina en redoble hacia la peluca
    t = PELUCA - BEAT
    for j in range(6):
        d("snare" if j < 4 else ("tomhi" if j == 4 else "tomlo"), t + j * BEAT / 6, 0.4 + 0.08 * j)
    # peluca: golpe y corte
    d("crash", PELUCA, 0.95)
    d("kick", PELUCA, 0.9)
    d("snare", PELUCA, 0.7)
    bajo(29, PELUCA, 1.0)
    # stop-time del cierre: un golpe de toda la banda por orden, el bajo sube
    for t, m, v in zip(ORDENES, [29, 33, 36, 41], [0.7, 0.75, 0.8, 1.0]):
        d("kick", t, v)
        d("snare", t, v * 0.9)
        bajo(m, t, 0.95, largo=0.5)
        if m == 41 and not libre:
            d("crash", t, 0.85)
    # DeLorean: redoble en crescendo hasta "LOS ONCE"
    t, n = ORDENES[-1] + 0.45, 0
    while t < LOS11 - 0.05:
        u = (t - ORDENES[-1]) / (LOS11 - ORDENES[-1])
        inst = "snare" if t < LOS11 - 0.45 else ("tomhi" if n % 2 == 0 else "tomlo")
        d(inst, t, 0.15 + 0.6 * u)
        t += BEAT / 3 if u < 0.6 else BEAT / 4
        n += 1
    # B: LOS ONCE -> blanco, swing de nuevo
    comp_b = int((BLANCO - LOS11) / BAR)
    if libre:
        d("kick", LOS11, 0.8)
        d("tomlo", LOS11, 0.6)
        tramo_libre(LOS11 + 0.2, BLANCO - BEAT, acentos)
        bajo_libre(LOS11, BLANCO - BEAT)
    else:
        swing(LOS11, comp_b, walking(comp_b, rnd), [LOS11])
    t = BLANCO - BEAT
    for j in range(4):
        d("tomhi" if j < 2 else "tomlo", t + j * BEAT / 4, 0.55 + 0.1 * j)
    # final: golpe largo en "blanco"
    d("crash", BLANCO, 1.0)
    d("kick", BLANCO, 1.0)
    bajo(29, BLANCO, 1.0)
    bajo(17 + 12, BLANCO + 0.002, 0.6)

    # sala chica: respuesta al impulso de ruido con caída exponencial (0.5 s), poca mezcla
    rng = np.random.default_rng(5)
    n = int((1.2 if libre else 0.5) * SR)
    ir = rng.normal(0, 1, n).astype("float32") * np.exp(-np.linspace(0, 7, n)).astype("float32")
    k_ir = 20 if libre else 6
    ir = np.convolve(ir, np.ones(k_ir) / k_ir, mode="same")          # sala oscura
    ir /= np.abs(ir).sum() / k_ir

    def sala(x):
        m = len(x) + len(ir)
        k = 1 << int(np.ceil(np.log2(m)))
        return np.fft.irfft(np.fft.rfft(x, k) * np.fft.rfft(ir, k), k)[:len(x)].astype("float32")

    w = 0.3 if libre else 0.14                                      # más aire en la libre
    L = P.L + w * sala(P.L)
    R = P.R + w * sala(P.R)
    L, R = L[:int(TOTAL * SR)], R[:int(TOTAL * SR)]
    pico = max(np.abs(L).max(), np.abs(R).max())
    est = (np.stack([L, R], 1) / pico * 0.89).astype("float32")
    salida = RAIZ / "musica" / ("intro86_jazz_libre.wav" if libre else "intro86_jazz_samples.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-af",
                    ("lowpass=f=7000,treble=g=-5:f=3500," if libre else "") + "loudnorm=I=-15:TP=-1.5:LRA=11", "-ar", str(SR), str(salida)], input=est.tobytes(), check=True)
    json.dump({"bpm": round(60 / BEAT, 2), "notas": P.notas}, open(salida.with_suffix(".json"), "w"), indent=1)
    midi(P.notas, salida.with_suffix(".mid"))
    print(f"{salida.name}: {TOTAL:.1f} s, {60 / BEAT:.1f} bpm, {len(P.notas)} notas")


def midi(notas, ruta):
    """MIDI tipo 0: batería en el canal 10 (mapa GM), contrabajo en el canal 1 (programa 32, acoustic bass)."""
    tpq, bpm = 480, 60 / BEAT
    ev = []
    for n in notas:
        tick = int(round(n["t"] / (60 / bpm) * tpq))
        vel = max(1, min(127, int(n["vel"] * 127)))
        if n["midi"] is None:
            continue
        if n["inst"] == "bass":
            ch, nota, largo = 0, n["midi"], int(n["dur"] / (60 / bpm) * tpq)
        else:
            ch, nota, largo = 9, n["midi"], 60
        ev.append((tick, 0x90 | ch, nota, vel))
        ev.append((tick + max(10, largo), 0x80 | ch, nota, 0))
    ev.sort(key=lambda e: (e[0], e[1] & 0xF0 == 0x90))

    def vlq(v):
        b = [v & 0x7F]
        while v > 0x7F:
            v >>= 7
            b.insert(0, (v & 0x7F) | 0x80)
        return bytes(b)
    us = int(60_000_000 / bpm)
    data = b"\x00\xff\x51\x03" + us.to_bytes(3, "big") + b"\x00\xc0\x20"
    ult = 0
    for tick, st, nota, vel in ev:
        data += vlq(max(0, tick - ult)) + bytes([st, nota, vel])
        ult = tick
    data += b"\x00\xff\x2f\x00"
    ruta.write_bytes(b"MThd" + struct.pack(">IHHH", 6, 0, 1, tpq) + b"MTrk" + struct.pack(">I", len(data)) + data)


if __name__ == "__main__":
    main()
